import json
import os
import time

import requests
from cryptography.fernet import Fernet
import config as cf



url = "https://api.mangadex.org"
authurl = "https://auth.mangadex.org"
lang = "en"
key = cf.MDKEY # this is fine to be just key since i'll create a seperate file for the MAL key.
username = cf.UNAME
password = cf.PASS
client_id = cf.CLI_ID

def writeTokens(tokenAccess, tokenRefresh, tokenRefreshExpiryDate, tokenAccessExpiryDate):
    with open("tokens.json", "w") as f:
        json.dump(data, f, indent=2)    
    data = {
        "accessToken": tokenAccess,
        "refreshToken": tokenRefresh,
        "accessTokenExpires": tokenAccessExpiryDate,
        "refreshTokenExpires": tokenRefreshExpiryDate
    }
    os.chmod("token.json", 0o600)

def updateAccessToken(tokenAccess, tokenAccessExpiryDate):
    try:
        with open("tokens.json", "r") as f:
            data = json.load(f)
            data["accessToken"] = tokenAccess
            data["accessTokenExpires"] = tokenAccessExpiryDate
        with open("tokens.json", "w") as f:
            json.dump(data, f, indent=2)
    except FileNotFoundError:
        print("File not found. Either delted or not created.")
        return None
    except Exception as e:
        print(f"An error occurred while updating the access token: {e}")
        return None

def getTokens():
    creds = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": client_id,
        "client_secret": key
    }

    r = requests.post(f"{authurl}/realms/mangadex/protocol/openid-connect/token", data=creds)

    r_json = r.json()

    accessToken = cf.EKEY.encrypt(r_json.get("access_token").encode())
    refreshToken = cf.EKEY.encrypt(r_json.get("refresh_token").encode())
    accessTokenExpires = time.time() + r_json.get("expires_in") 
    refreshTokenExpires = time.time() + r_json.get("refresh_expires_in")

    writeTokens(accessToken, refreshToken, refreshTokenExpires, accessTokenExpires)
    
def refreshTokens(refresh_token):
    creds = {
        "grant_type": "refresh_token",
        "refresh_token": cf.EKEY.decrypt(refresh_token),
        "client_id": client_id,
        "client_secret": key
        }
    r = requests.post(f"{authurl}/realms/mangadex/protocol/openid-connect/token", data=creds)
    r_json = r.json()
    newAccessToken = cf.EKEY.encrypt(r_json.get("access_token").encode())
    newAccessExpiration = time.time() + r_json.get("expires_in")
    updateAccessToken(newAccessToken, newAccessExpiration)
