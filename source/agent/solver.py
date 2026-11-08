
import re
import sys
import time
from collections import Counter

from . import config
from .formatter import finalize, is_valid
from .llm import chat, LLMError
from .prompts import CODE_SYSTEM, COT_SYSTEM, build_hint
from .sandbox import run_code_detailed


def _log(*parts):
    print("[agent]", *parts, file=sys.stderr, flush=True)


def _debug_code(tag, code, raw=None):
    import os
    if os.getenv("AGENT_DEBUG") == "1":
        print(f"[debug] ---- {tag} code ----\n{code}\n[debug] raw output: {raw!r}",
              file=sys.stderr, flush=True)


def _extract_code(text):
    blocks = re.findall(
        r"```(?:python|py)?\s*\n(.*?)```",
        text or "",
        re.S | re.I
    )
    if blocks:
        return max(blocks, key=len)

    if "print(" in (text or ""):
        return text

    return None


def _code_user(problem, variant=0):
    hint = build_hint(problem)
    msg = "PROBLEM:\n" + problem
    if hint:
        msg += "\n\nGUIDANCE (apply only what is relevant):\n" + hint
    if variant == 1:
        msg += "\n\nUse a different encoding of the constraints than the obvious one, then verify."
    return "Write the Python program that solves this.\n\n" + msg


def _generate_code(problem, temperature, timeout, variant=0):
    response = chat(
        CODE_SYSTEM,
        _code_user(problem, variant),
        temperature=temperature,
        max_tokens=config.CODE_TOKENS,
        think=config.CODE_THINK,
        timeout=timeout
    )

    code = _extract_code(response)

    if not code:
        return None, None, "Model response did not contain a Python program."

    raw, error = run_code_detailed(code)
    _debug_code("generate", code, raw if not error else error)

    if error:
        return None, code, error

    answer = finalize(problem, raw)

    if not is_valid(problem, answer):
        return None, code, (
            f"Program output failed answer-format validation: {raw!r}"
        )

    return answer, code, None


def _repair_code(problem, previous_code, diagnostic, timeout):
    repair_system = CODE_SYSTEM + """
You are repairing a previous program.
Fix the specific error and reconsider all original constraints.
Do not assume a unique solution without checking all candidates.
Return exactly one fenced Python code block.
"""

    prompt = (
        "ORIGINAL PROBLEM:\n" + problem +
        "\n\nPREVIOUS PROGRAM:\n```python\n" + (previous_code or "") +
        "\n```\n\nEXECUTION / VALIDATION ERROR:\n" + diagnostic
    )

    response = chat(
        repair_system,
        prompt,
        temperature=0.0,
        max_tokens=config.CODE_TOKENS,
        think=config.CODE_THINK,
        timeout=timeout
    )

    code = _extract_code(response)

    if not code:
        return None, "Repair response did not contain Python code."

    raw, error = run_code_detailed(code)

    if error:
        return None, error

    answer = finalize(problem, raw)

    if not is_valid(problem, answer):
        return None, f"Repaired output failed format validation: {raw!r}"

    return answer, None


def _cot_attempt(problem, timeout, lenient=False):
    out = chat(
        COT_SYSTEM,
        "PROBLEM:\n" + problem,
        temperature=0.0,
        max_tokens=config.COT_TOKENS,
        think=config.COT_THINK,
        timeout=timeout
    )

    match = re.findall(r"FINAL\s*:\s*(.+)", out, re.I)

    answer = finalize(
        problem,
        match[-1] if match else out
    )

    if is_valid(problem, answer):
        return answer
    # lenient: any non-empty single-line answer beats an empty output
    if lenient and answer and "\n" not in answer and len(answer) < 200:
        return answer
    return None


def solve(problem: str) -> str:
    if not isinstance(problem, str) or not problem.strip():
        return ""

    started = time.time()
    votes = Counter()
    calls = 0
    repaired = False

    # Limit unnecessary candidate generation.
    sample_limit = min(config.MAX_CODE_SAMPLES, 3)

    def remaining():
        return config.TIME_BUDGET - (time.time() - started)

    def call_timeout():
        return max(
            1,
            min(config.REQUEST_TIMEOUT, int(remaining()))
        )

    for index in range(sample_limit):

        if remaining() < 15 or calls >= config.MAX_LLM_CALLS:
            break

        try:
            temperature = [0.0, 0.3, 0.5][index]

            calls += 1

            answer, code, error = _generate_code(
                problem,
                temperature,
                call_timeout(),
                variant=1 if index == 2 else 0
            )

            _log(
                f"code#{index}",
                repr(answer),
                "error=",
                repr(error)
            )

            if answer:
                votes[answer] += 1

                # Two independent candidates agree.
                if votes[answer] >= 2:
                    _log("consensus", repr(answer))
                    return answer

            elif (
                not repaired
                and error
                and remaining() > 25
                and calls < config.MAX_LLM_CALLS
            ):
                repaired = True
                calls += 1

                fixed, repair_error = _repair_code(
                    problem,
                    code,
                    error,
                    call_timeout()
                )

                _log(
                    "repair",
                    repr(fixed),
                    "error=",
                    repr(repair_error)
                )

                if fixed:
                    votes[fixed] += 1

                    if votes[fixed] >= 2:
                        return fixed

        except LLMError as exc:
            _log("llm error", exc)
            break

        except Exception as exc:
            _log(
                "unexpected solver error",
                type(exc).__name__,
                exc
            )
            break

    # Select the strongest program candidate.
    if votes:
        answer, count = votes.most_common(1)[0]

        _log(
            "best candidate",
            repr(answer),
            "votes=",
            count,
            "all_votes=",
            dict(votes)
        )

        return answer

    # Reasoning fallback if program generation failed.
    if remaining() > 25 and calls < config.MAX_LLM_CALLS:
        try:
            calls += 1

            answer = _cot_attempt(
                problem,
                call_timeout(),
                lenient=True
            )

            _log("cot", repr(answer))

            if answer:
                return answer

        except LLMError as exc:
            _log("llm error", exc)

        except Exception as exc:
            _log("cot error", type(exc).__name__, exc)

    return ""
