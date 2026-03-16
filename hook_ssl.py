"""
PyInstaller runtime hook — runs inside the exe before any user code.
Points Python's ssl module at the certifi CA bundle that we bundled
into the exe, fixing SSL_CERTIFICATE_VERIFY_FAILED on Windows.
"""
import os
import sys

def _fix_ssl():
    try:
        import certifi
        ca_bundle = certifi.where()
        os.environ.setdefault("SSL_CERT_FILE",      ca_bundle)
        os.environ.setdefault("REQUESTS_CA_BUNDLE",  ca_bundle)
        os.environ.setdefault("CURL_CA_BUNDLE",      ca_bundle)
    except Exception:
        pass   # certifi not available — ssl fallback in game code handles it

_fix_ssl()
