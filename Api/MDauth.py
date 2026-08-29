import json
import time

import requests
from cryptography.fernet import Fernet
from config import * 



lang = "en"
key = MDKEY # this is fine to be just key since i'll create a seperate file for the MAL key.
username = UNAME
password = PASS
client_id = CLI_ID

def writeTokens(tokenAccess, tokenRefresh, tokenRefreshExpiryDate, tokenAccessExpiryDate):
    data = {
        "accessToken": tokenAccess,
        "refreshToken": tokenRefresh,
        "accessTokenExpires": tokenAccessExpiryDate,
        "refreshTokenExpires": tokenRefreshExpiryDate
    }
    
    with open("token.json", "w") as f:
        json.dump(data, f, indent=2)    


def updateAccessToken(tokenAccess, tokenAccessExpiryDate):
    try:
    
        with open("token.json", "r") as f:
            data = json.load(f)
            data["accessToken"] = tokenAccess
            data["accessTokenExpires"] = tokenAccessExpiryDate
        with open("token.json", "w") as f:
            json.dump(data, f, indent=2)
    
    except FileNotFoundError:
        print("File not found. Either deleted or not created.")
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

    r = requests.post(f"{auth}/realms/mangadex/protocol/openid-connect/token", data=creds)
    r_json = r.json()

    accessToken = r_json.get("access_token")
    refreshToken = EKEY.encrypt(r_json.get("refresh_token").encode()).decode()

    accessTokenExpires = time.time() + r_json.get("expires_in") 
    refreshTokenExpires = time.time() + r_json.get("refresh_expires_in")

    writeTokens(accessToken, refreshToken, refreshTokenExpires, accessTokenExpires)
    
def refreshTokens(refresh_token):
    creds = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token.decode(),
        "client_id": client_id,
        "client_secret": key
        }

    r = requests.post(f"{auth}/realms/mangadex/protocol/openid-connect/token", data=creds)
    r_json = r.json()

    newAccessToken = r_json.get("access_token")
    newAccessExpiration = time.time() + r_json.get("expires_in")
    
    updateAccessToken(newAccessToken, newAccessExpiration)
    
def isTokenValid():
    try:
        with open("token.json", "r") as f:
            data = json.load(f)
            if  data == {}:
                getTokens()
                print("No Tokens exist, got Tokens")
                return True
            elif data["refreshTokenExpires"] <= time.time()-90:
                getTokens()
                print("No Valid Tokens exist, got new ones")
                return True
            elif data["accessTokenExpires"] <= time.time()-90 :
                refreshTokens(EKEY.decrypt(data["refreshToken"].encode()))
                print("Access token out of date, got new Token")
                return True
            
            
    except FileNotFoundError:
        print("Token file doesn't exist")
        with open("token.json", "w") as f:
            f.write("{}")
        return isTokenValid()
    except PermissionError:
        print("Don't have permission to read token file")
    except IsADirectoryError:
        print("token.json is a directory, not a file")
    except UnicodeDecodeError:
        print("File encoding issue")
    except OSError as e:
        print(f"OS error: {e}")
    except Exception as e:
        print(f"Unexpected error:")
        print(repr(e))
