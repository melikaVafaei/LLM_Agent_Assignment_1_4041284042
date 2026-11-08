import re
import sys
import time

import requests

from . import config

_session = requests.Session()
_resolved_model = None


class LLMError(RuntimeError):
    pass


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

def chat(system, user, temperature=0.0, max_tokens=2500, think=False, timeout=None):
    _check_local()
    payload = {
        "model": _model(),
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "stream": False,
        "think": think,
        "keep_alive": "30m",
        "options": {"temperature": temperature, "num_ctx": config.NUM_CTX,
                    "num_predict": max_tokens, "top_p": 0.9},
    }
    t0 = time.time()
    last = None
    for attempt in range(2):
        try:
            r = _session.post(config.HOST + "/api/chat", json=payload,
                              timeout=timeout or config.REQUEST_TIMEOUT)
            r.raise_for_status()
            msg = r.json()["message"]
            out = strip_think(msg.get("content") or "")
            print(f"[llm] {time.time()-t0:.1f}s think={think} chars={len(out)}", file=sys.stderr)
            return out
        except requests.exceptions.Timeout as exc:
            raise LLMError(f"timeout: {exc}")  # retrying would only burn the time budget
        except Exception as exc:
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
