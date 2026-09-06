import requests
import config 
import json

import Api.Mal.auth as api

from pathlib import Path

class reqMal:
    def __init__(self):
        self.url ="https://api.myanimelist.net/v2/"

        

    def verify(self):
        return api.verifyTokens()

    def getMangaList(self):
        if self.verify():
            with open("token.json", "r") as f:
                tokenData = json.load(f)
            AT = tokenData["access_token"]
            headers = {
            "Authorization": f"Bearer {AT}"
            }
            
            r=requests.get(
                f"{self.url}users/@me/mangalist",
                headers=headers,
                params={
                    "limit": 100,
                    "sort": "manga_title",
                    "fields": "alternative_titles"
                }
            )
            print(r)
            with open("mangaList.json", "w") as f:
                json.dump(r.json(), f, indent=2)
    

