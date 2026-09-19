import requests
import json

from API.Mal.auth import getAccessToken
from config import tokenPath
from pathlib import Path

class reqMal:
    def __init__(self):
        self.url ="https://api.myanimelist.net/v2"

    def headers(self):
        return {"Authorization": f"Bearer {getAccessToken()}"}


    def getAnimeList(self):        
        r=requests.get(f"{self.url}/users/@me/animelist",
            headers=self.headers,
            params={
                "sort": "anime_title",
                "fields": "alternative_titles, my_list_status",
                "limit": 100,
            }
        )
        r.raise_for_status()
        
        with open("JsonIO/animeList.json", "w") as f:
            json.dump(r.json(), f, indent=2)
        print(f"Successfully fetched {len(r.json()['data'])} anime entries")
        return r.json()

    def updateMal(self, query, watchedEpisode):
        with open ("JsonIO/aEnTitles.json", "r") as f:
            data = json.load(f)

        results=[]

        for _, info in data.items():
            for title in info["titles"]:
                if query.lower() in title.lower():
                    results.append(info)
                    break

        if not results:
            return print("Title is not in the titles json. [HOW?]")
        result = results[0]
        animeId = result["id"]

        r = requests.patch(
            f"{self.url}/anime/{animeId}/my_list_status",
            
            headers=self.headers,
            data={
                "num_episodes_watched": watchedEpisode,
            }
        )
        if not r:
            return False
        return True