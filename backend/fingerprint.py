"""Group similar errors by hashing a normalized signature.

Why normalize? Two "same" errors often differ by a memory address, line number,
or object id in the stack trace. Hashing the raw string would scatter them
across many issues. We strip those tokens before hashing.
"""
import hashlib
import re

_MEM_ADDR = re.compile(r"0x[0-9a-fA-F]+")
_LINE_NUM = re.compile(r":\d+")
_PY_OBJECT = re.compile(r"<[\w\.]+ object at 0x[0-9a-fA-F]+>")
_DIGIT_RUN = re.compile(r"\b\d{3,}\b")  # long numeric ids like request/user ids


def normalize(frame: str) -> str:
    if not frame:
        return ""
    s = _PY_OBJECT.sub("<object>", frame)
    s = _MEM_ADDR.sub("0xADDR", s)
    s = _LINE_NUM.sub(":LINE", s)
    s = _DIGIT_RUN.sub("N", s)
    return s.strip()


def extract_exception_type(message: str) -> str:
    """Pull the exception class out of a 'KeyError: foo' style message."""
    if not message:
        return "UnknownError"
    head = message.split(":", 1)[0].strip()
    return head or "UnknownError"


def extract_first_frame(stack: str) -> str:
    """Return the deepest meaningful stack-trace line.

    Python tracebacks list the deepest frame LAST, so we scan from the end
    for the first 'File "..."' line that isn't inside stdlib.
    """
    if not stack:
        return ""
    lines = [ln.strip() for ln in stack.splitlines() if ln.strip()]
    for ln in reversed(lines):
        if ln.startswith("File ") and "site-packages" not in ln:
            return ln
    return lines[-1] if lines else ""


def fingerprint(app: str, exception_type: str, first_frame: str) -> str:
    """SHA-256 hex, truncated to 16 chars (plenty for a demo scale)."""
    sig = f"{app}|{exception_type}|{normalize(first_frame)}"
    return hashlib.sha256(sig.encode("utf-8")).hexdigest()[:16]
