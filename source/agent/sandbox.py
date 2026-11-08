import os
import subprocess
import sys
import tempfile
from . import config

_PRELUDE = """
import sys
try:
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (1<<30, 1<<30))
except Exception:
    pass
"""

_BANNED = (
    "import socket", "import requests", "import urllib",
    "import subprocess", "import shutil", "os.system",
    "os.remove", "os.unlink", "rmtree", "__import__",
    "import http", "open("
)

def _env():
    keep = ("PATH", "SYSTEMROOT", "SystemRoot", "TEMP", "TMP", "TMPDIR")
    return {k: os.environ[k] for k in keep if k in os.environ}

def run_code_detailed(code, timeout=None):
    timeout = timeout or config.SANDBOX_TIMEOUT
    if not isinstance(code, str) or not code.strip():
        return None, "No Python code was extracted."

    for token in _BANNED:
        if token in code:
            return None, f"Sandbox policy rejected code containing: {token}"

    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "prog.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(_PRELUDE + "\n" + code)

        try:
            proc = subprocess.run(
                [sys.executable, "-I", path],
                capture_output=True, text=True, timeout=timeout,
                cwd=directory, env=_env()
            )
        except subprocess.TimeoutExpired:
            return None, f"Program exceeded sandbox timeout ({timeout}s)."
        except Exception as exc:
            return None, f"Sandbox launch error: {type(exc).__name__}: {exc}"

        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "No error output").strip()
            return None, f"Program exit code {proc.returncode}: {detail[-1800:]}"

        lines = [x.strip() for x in proc.stdout.splitlines() if x.strip()]
        if len(lines) != 1:
            return None, (
                f"Expected exactly one non-empty output line; got {len(lines)}. "
                f"stdout={proc.stdout[-1000:]!r}"
            )
        return lines[0], None

def run_code(code, timeout=None):
    output, error = run_code_detailed(code, timeout)
    return output
