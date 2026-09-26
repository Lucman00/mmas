import base64
import json
import os
import secrets
import threading
import time
import webbrowser

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlencode, urlparse, parse_qs

import requests

from config import EKEY, TOKEN_PATH, get_client_id


AUTH_URL             = "https://myanimelist.net/v1/oauth2/authorize"
TOKEN_URL            = "https://myanimelist.net/v1/oauth2/token"
REDIRECT_URI         = "http://localhost:8080/callback"
PORT = 8080
REFRESH_WARN_SECONDS   = 24 * 3600 # pretty much the time when you should refresh your tokens.

def _load_tokens() -> dict | None:
    if not TOKEN_PATH.exists():
        return None
    try:
        blob = TOKEN_PATH.read_bytes()
        return json.loads(EKEY.decrypt(blob).decode())
    except Exception:
        return None

def _save_tokens(data: dict) -> None:
    blob = EKEY.encrypt(json.dumps(data).encode())
    TOKEN_PATH.write_bytes(blob)
    try:
        os.chmod(TOKEN_PATH, 0o600)
    except OSError:
        pass



def _b64_url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _new_pkce_pair() -> tuple[str, str]:
    verifier    = _b64_url(secrets.token_bytes(64))
    return verifier, verifier

class _CallBackHandler(BaseHTTPRequestHandler):
    captured:dict = {}

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != urlparse(REDIRECT_URI).path:
            self.send_response(404); self.end_headers(); return

        params = parse_qs(parsed.query)
        _CallBackHandler.captured = {
            "code" : params.get("code" , [None])[0],
            "state": params.get("state", [None])[0],
            "error": params.get("error", [None])[0],
        }
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<h2>You can close this tab and return to the terminal.</h2>")

        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def log_message(self, *a, **k):
        pass

def _wait_for_callback(timeout: int = 300) -> dict:
    _CallBackHandler.captured = {}
    server = ThreadingHTTPServer(("127.0.0.1", PORT), _CallBackHandler)
    server.timeout = timeout

    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    t.join(timeout)
    server.server_close()
    return _CallBackHandler.captured


def run_oauth_flow(no_browser:bool = False) -> dict:
    verifier, challenge = _new_pkce_pair()
    state = _b64_url(secrets.token_bytes(16))
    client_id = get_client_id()

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "code_challenge": challenge,
        "code_challenge_method": "plain",
        "state": state,
    }
    url = f"{AUTH_URL}?{urlencode(params)}"

    if no_browser:
        print(f"Open the following URL in your browser (on any machine):\n {url} \nAfter authorizing, MAL will redirect to {REDIRECT_URI} \n",
              "which won't load. Copy the 'code=' value out of the URL bar and paste it here.")
        code = input("code: ").strip()
    else:
        print("Opening browser for MAL authorization...")
        webbrowser.open(url)
        captured = _wait_for_callback()
        if captured.get("error"):
            raise RuntimeError(f"OAuth error: {captured['error']}")
        if captured.get("state") != state:
            raise RuntimeError("state mismatch, possible CSRF, aborting")
        code = captured.get("code")

    if not code:
        raise RuntimeError("No authorization code received")

    r = requests.post(
        TOKEN_URL,
        auth=(client_id, ""),
        data={
            "grant_type":       "authorization_code",
            "code":             code,
            "redirect_uri":     REDIRECT_URI,
            "code_verifier":    verifier,
        }
    )
    r.raise_for_status()
    tok = r.json()
    tok["verifier"]         = verifier
    tok["obtained_at"]       = time.time()
    tok["refresh_obtained_at"]= time.time()
    tok["access_expires_at"]  = time.time() + tok["expires_in"]
    tok["refresh_expires_at"] = time.time() + tok.get("refresh_token_expires_in", 30*24*3600)
    _save_tokens(tok)
    return tok

def _refresh_tokens(tok: dict) -> dict:
    client_id    = get_client_id()
    r           = requests.post(
        TOKEN_URL,
        auth=(client_id, ""),
        data={
        "grant_type":       "refresh_token",
        "refresh_token":    tok["refresh_token"],
    })
    if r.status_code == 400 and "invalid_grant" in r.text:
        raise RuntimeError("refresh token expired. Reauthorize yourself")
        
    r.raise_for_status()
    new = r.json()

    new["verifier"]         =tok.get("verifier", "")
    new["obtained_at"]       = time.time()
    new["refresh_obtained_at"]= time.time()
    new["access_expires_at"]  = time.time() + new["expires_in"]
    new["refresh_expires_at"] = time.time() + new.get("refresh_token_expires_in", 30*24*3600)
    _save_tokens(new)
    return new

def get_access_token(interactive: bool = True) -> str:
    tok= _load_tokens()

    if tok is None:
        if not interactive:
            raise RuntimeError("No tokens and not allowed to run OAuth flow")
        tok = run_oauth_flow()

    if time.time() > tok["access_expires_at"] - 300:
        try:
            tok = _refresh_tokens(tok)
        except RuntimeError:
            if not interactive:
                raise
            print("Refresh token expired. Re-authorizing...")
            tok = run_oauth_flow()

    elif time.time() > tok["refresh_expires_at"] - REFRESH_WARN_SECONDS:
        try:
            tok = _refresh_tokens(tok)
        except RuntimeError:
            if not interactive:
                raise
            print("Refresh token expired. Re-authorizing...")
            tok = run_oauth_flow()
    return tok["access_token"]










