"""Tiny LogVault client. Drop into any Python app:

    from logvault_client import LogVault
    lv = LogVault("http://localhost:5000", app="payments", api_key="demo-key-payments")
    try:
        risky()
    except Exception:
        lv.capture_exception()
"""
import json
import os
import sys
import traceback
import urllib.error
import urllib.request


class LogVault:
    def __init__(self, base_url: str, app: str, api_key: str, timeout: float = 2.0):
        self.base_url = base_url.rstrip("/")
        self.app = app
        self.api_key = api_key
        self.timeout = timeout

    def capture(self, message: str, severity: str = "ERROR", stack: str = "") -> dict:
        payload = {
            "app": self.app,
            "severity": severity,
            "message": message,
            "stack": stack,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/log",
            data=data,
            method="POST",
            headers={"Content-Type": "application/json", "X-API-Key": self.api_key},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}", "detail": e.read().decode("utf-8", "ignore")}
        except Exception as e:
            # Error-reporting failures must never crash the host app.
            return {"error": str(e)}

    def capture_exception(self, severity: str = "ERROR") -> dict:
        exc_type, exc_val, exc_tb = sys.exc_info()
        if exc_type is None:
            return {"error": "no active exception"}
        stack = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
        message = f"{exc_type.__name__}: {exc_val}"
        return self.capture(message=message, severity=severity, stack=stack)


if __name__ == "__main__":
    lv = LogVault(
        base_url=os.getenv("LOGVAULT_URL", "http://localhost:5000"),
        app=os.getenv("LOGVAULT_APP", "payments"),
        api_key=os.getenv("LOGVAULT_API_KEY", "demo-key-payments"),
    )
    try:
        raise ValueError("sanity check from logvault_client.py __main__")
    except Exception:
        print(lv.capture_exception())
