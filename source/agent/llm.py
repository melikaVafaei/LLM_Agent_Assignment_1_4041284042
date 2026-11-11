import json
import re
import sys
import time

import requests

from . import config

_session = requests.Session()
_resolved_model = None


class LLMError(RuntimeError):
    partial = ""


def _check_local():
    host = config.HOST
    if not re.match(r"^https?://(127\.0\.0\.1|localhost)(:\d+)?/?$", host):
        raise LLMError("Only a local Ollama server is allowed.")


def strip_think(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    return re.sub(r"^.*?</think>", "", text, flags=re.S).strip()


def _model():
    """Use only the explicitly configured model; never silently substitute."""
    global _resolved_model
    if _resolved_model:
        return _resolved_model
    _resolved_model = config.MODEL
    try:
        response = _session.get(config.HOST + "/api/tags", timeout=10)
        response.raise_for_status()
        names = [m["name"] for m in response.json().get("models", [])]
        accepted = {config.MODEL, config.MODEL + ":latest"}
        if names and not any(name in accepted for name in names):
            raise LLMError(
                f"Required model {config.MODEL!r} is not installed. "
                f"Installed models: {names}"
            )
    except LLMError:
        raise
    except Exception as exc:
        print(f"[llm] Could not verify installed model: {exc}", file=sys.stderr)
    return _resolved_model

_CODE_DONE = re.compile(r"```(?:python|py)?[ \t]*\n.*?```", re.S | re.I)


def _code_complete(buf):
    """True once the reply contains one complete fenced code block (outside <think>)."""
    if "<think>" in buf and "</think>" not in buf:
        return False
    return bool(_CODE_DONE.search(strip_think(buf)))


def chat(system, user, temperature=0.0, max_tokens=2500, think=False, timeout=None,
         stop_at_code=False):
    """Streams the reply. With stop_at_code the request is closed as soon as the first
    code block ends, so no time is wasted on explanations after the code.
    On timeout the partial reply is attached to the exception (exc.partial)."""
    _check_local()
    payload = {
        "model": _model(),
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "stream": True,
        "think": think,
        "keep_alive": "30m",
        "options": {"temperature": temperature, "num_ctx": config.NUM_CTX,
                    "num_predict": max_tokens, "top_p": 0.9},
    }
    t0 = time.time()
    limit = timeout or config.REQUEST_TIMEOUT
    deadline = t0 + limit
    last = None
    for attempt in range(2):
        buf = []
        try:
            with _session.post(config.HOST + "/api/chat", json=payload, stream=True,
                               timeout=(10, limit)) as r:
                r.raise_for_status()
                for line in r.iter_lines(chunk_size=1):
                    if time.time() > deadline:
                        raise requests.exceptions.Timeout("overall deadline reached")
                    if not line:
                        continue
                    chunk = json.loads(line)
                    if chunk.get("error"):
                        raise RuntimeError(chunk["error"])
                    buf.append((chunk.get("message") or {}).get("content") or "")
                    if stop_at_code and _code_complete("".join(buf)):
                        break
                    if chunk.get("done"):
                        break
            out = strip_think("".join(buf))
            print(f"[llm] {time.time()-t0:.1f}s think={think} chars={len(out)}", file=sys.stderr)
            return out
        except Exception as exc:
            # In streaming mode requests reports a read timeout as ConnectionError,
            # so detect timeouts by type or by message.
            if isinstance(exc, requests.exceptions.Timeout) or "timed out" in str(exc).lower():
                err = LLMError(f"timeout: {exc}")  # retrying would only burn the time budget
                err.partial = strip_think("".join(buf)) if buf else ""
                raise err
            last = exc
            if "think" in str(exc).lower() or (getattr(exc, "response", None) is not None
                                                and exc.response.status_code == 400):
                payload.pop("think", None)  # older Ollama / model without think support
            time.sleep(1)
    raise LLMError(str(last))


def warmup(timeout=900):
    """Load the model into memory once (cold start can take minutes on big models).
    Skipped quickly if the model is already resident."""
    _check_local()
    try:
        ps = _session.get(config.HOST + "/api/ps", timeout=5).json().get("models", [])
        if any(m.get("name", "").startswith(config.MODEL) for m in ps):
            return True
    except Exception:
        pass
    try:
        _session.post(config.HOST + "/api/chat", json={
            "model": _model(), "messages": [{"role": "user", "content": "hi"}],
            "stream": False, "think": False, "keep_alive": "30m",
            "options": {"num_predict": 1, "num_ctx": config.NUM_CTX}}, timeout=timeout)
        return True
    except Exception as exc:
        print(f"[llm] warmup failed: {exc}", file=sys.stderr)
        return False