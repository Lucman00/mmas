import base64
import hashlib
import json
import os
import secrets
import threading
import time
import webbrowser

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlencode, urlparse, parse_qs

import requests

from config import EKEY, TOKENPATH, getClientId


AUTHURL             = "https://myanimelist.net/v1/oauth2/authorize"
TOKENURL            = "https://myanimelist.net/v1/oauth2/token"
REDIRECTURI         = "http://localhost:8080/callback"
PORT = 8080
REFRESWARNSECONDS   = 24 * 3600 # pretty much the time when you should refresh your tokens.

def loadTokens() -> dict | None:
    if not TOKENPATH.exists():
        return None
    try:
        blob = TOKENPATH.read_bytes()
        return json.loads(EKEY.decrypt(blob).decode())
    except Exception:
        return None

def saveTokens(data: dict) -> None:
    blob = EKEY.encrypt(json.dumps(data).encode)
    TOKENPATH.write_bytes(blob)
    try:
        os.chmod(TOKENPATH, 0o600)
    except OSError:
        pass



def b64Url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def newPkcePair() -> tuple[str, str]:
    verifier    = b64Url(secrets.token_bytes(64))
    challenge   = b64Url(hashlib.sha256(verifier.encode()).digest())
    return verifier, challenge

class callBackHandler(BaseHTTPRequestHandler):
    captured:dict = {}

    def doGET(self):
        parsed = urlparse(self.path)
        if parsed.path != urlparse(REDIRECTURI).path:
            self.send_response(404); self.end_headers(); return

        params = parse_qs(parsed.query)
        callBackHandler.captured = {
            "code" : params.get("code" , [None])[0],
            "state": params.get("state", [None])[0],
            "error": params.get("error", [None])[0],
        }
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<h2>You can close this tab and return to the terminal.</h2>")

        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def logMessage(self, *a, **k):
        pass

def waitForCallback(timeout: int = 300) -> dict:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), callBackHandler)
    server.timeout = timeout

    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    t.join(timeout)
    server.server_close()
    return callBackHandler.captured


def runOauthFlow(noBrowser:bool = False) -> dict:
    verifier, challenge = newPkcePair()
    state = b64Url(secrets.token_bytes(16))
    clientId = getClientId()

    params = {
        "response_type": "code",
        "client_id": clientId,
        "redirect_uri": REDIRECTURI,
        "code_challenge": challenge,
        "code_challenge_method": "s256",
        "state": state,
    }
    url = f"{AUTHURL}?{urlencode(params)}"

    if noBrowser:
        print(f"Open the following URL in your browser (on any machien):\n {url} \nAfter authorizing, MAL will redirect to {REDIRECTURI} \n",
              "which won't load. Copy the 'code=' value out of the URL bar and paste it here.")
        code = input("code: ").strip()
        returnedState = state
    else:
        print("Opening browser for MAL authorization...")
        webbrowser.open(url)
        captured = waitForCallback()
        if captured.get("error"):
            raise RuntimeError(f"OAuth error: {captured['error']}")
        if captured.get("state") != state:
            raise RuntimeError("state mismatch, possible CSRF, aborting")
        code = captured.get("code")

    if not code:
        raise RuntimeError("No authorization code received")

    r = requests.post(TOKENURL, data={
        "grant_type":       "authorization_code",
        "code":             code,
        "redirect_uri":     REDIRECTURI,
        "client_id":        clientId,
        "code_verifier":    verifier,
    })
    r.raise_for_status()
    tok = r.json()
    tok["verifier"]         = verifier
    tok["obtainedAt"]       = time.time()
    tok["refreshObtainedAt"]= time.time()
    tok["accessExpiresAt"]  = time.time() + tok["expires_in"]
    tok["refreshExpiresAt"] = time.time() + tok.get("refresh_token_expires_in", 30*24*3600)
    saveTokens(tok)
    return tok

def refreshTokens(tok: dict) -> dict:
    clientId    = getClientId()
    r           = requests.post(TOKENURL, data={
        "grant_type":       "refresh_token",
        "refresh_token":    tok["refresh_token"],
        "client_id":        clientId
    })
    if r.status_code == 400 and "invalid_grant" in r.text:
        raise RuntimeError("refresh token expired. Reauthorize yourself")
        
    r.raise_for_status()
    new = r.json()

    new["verifier"]         =tok.get("verifier", "")
    new["obtainedAt"]       = time.time()
    new["refreshObtainedAt"]= time.time()
    new["accessExpiresAt"]  = time.time() + new["expires_in"]
    new["refreshExpiresAt"] = time.time() + new.get("refresh_token_expires_in", 30*24*3600)
    saveTokens(new)
    return new

def getAccessToken(interactive: bool = True) -> str:
    tok= loadTokens()

    if tok is None:
        if not interactive:
            raise RuntimeError("No tokens and not allowed to run OAuth flow")
        tok = runOauthFlow()

    if time.time() > tok["accessExpiresAT"] - 300:
        try:
            tok = refreshTokens(tok)
        except RuntimeError:
            if not interactive:
                raise
            print("Refresh token expired. Re-authorizing")
            tok = runOauthFlow()

    if time.time() > tok["refreshExpiresAt"] - REFRESWARNSECONDS:
        tok = refreshTokens(tok)

    return tok["access_token"]

def verifyTokens() -> bool:
    try: 
        getAccessToken()
        return True
    except Exception as e:
        print(f"auth failed: {e}")
        return False
















