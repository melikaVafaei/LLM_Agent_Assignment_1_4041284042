import os

def _f(name, default, cast=str):
    try:
        return cast(os.getenv(name, default))
    except ValueError:
        return cast(default)

MODEL = _f("OLLAMA_MODEL", "qwen3.8:27b")
HOST = _f("OLLAMA_HOST", "http://127.0.0.1:11434")
NUM_CTX = _f("OLLAMA_CONTEXT", "3072", int)
REQUEST_TIMEOUT = _f("REQUEST_TIMEOUT", "300", int)

TIME_BUDGET = _f("TIME_BUDGET", "240", float)        # seconds per problem
MAX_CODE_SAMPLES = _f("MAX_CODE_SAMPLES", "5", int)  # code-writing calls
MAX_LLM_CALLS = _f("MAX_LLM_CALLS", "8", int)
CODE_TOKENS = _f("CODE_TOKENS", "1000", int)
COT_TOKENS = _f("COT_TOKENS", "1200", int)
CODE_THINK = _f("CODE_THINK", "0") == "1"   # thinking mode for code generation
COT_THINK = _f("COT_THINK", "0") == "1"     # thinking mode for fallback reasoning
SANDBOX_TIMEOUT = _f("SANDBOX_TIMEOUT", "10", float)