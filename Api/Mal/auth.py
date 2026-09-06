import requests
import webbrowser
import json
import time 

from cryptography.fernet import Fernet
from pathlib import Path
from config import key, cid, reurl, EKEY


url ="https://myanimelist.net/v1/oauth2"
def getTokens():
    
    with open("token.json", "r") as f:
        tokenData = json.load(f)
        
    verifier = EKEY.decrypt(tokenData["verifier"].encode()).decode()

    r = requests.post(
        f"{url}/token",
        data={
            "client_id": cid,
            "client_secret": key,
            "grant_type": "refresh_token",
            "refresh_token": tokenData["refresh_token"],
            "code_verifier": verifier
        }
    )    
    r.raise_for_status()
    nTokenData = r.json()
    nTokenData["verifier"] = EKEY.encrypt(verifier.encode()).decode()
    nTokenData["received_at"] = time.time()
    nTokenData["expires_at"] = time.time() + nTokenData["expires_in"]
    
    with open("token.json", "w") as f:
        json.dump(nTokenData, f, indent=2)
    
def verifyTokens():
    
    if Path("token.json").exists():
        with open("token.json") as f:
            data = json.load(f)
        if time.time() + 120 >= data["expires_at"]:
            print("token expired. Generating new one")
            getTokens()
        return True
    print("you lost your tokens. ggs")
    return False