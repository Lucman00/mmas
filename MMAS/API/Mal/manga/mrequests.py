import requests
import json

from API.Mal.auth import getAccessToken
from pathlib import Path

class reqMal:
    def __init__(self):
        self.url ="https://api.myanimelist.net/v2"

    def headers(self):
        return {"Authorization": f"Bearer {getAccessToken()}"}

    def getMangaList(self):
        r=requests.get(
            f"{self.url}/users/@me/mangalist",
            headers=self.headers(),
            params={
                "sort": "manga_title",
                "fields": "alternative_titles, my_list_status"
            }
        )
        r.raise_for_status()
        
        with open("JsonIO/mangaList.json", "w") as f:
            json.dump(r.json(), f, indent=2)
        print(f"Successfully fetched {len(r.json()['data'])} manga entries")
        return r.json()

    def updateMal(self, query, readChapter):
        with open ("JsonIO/enTitles.json", "r") as f:
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
        mangaID = result["id"]

        r = requests.patch(
            f"{self.url}/manga/{mangaID}/my_list_status",
            
            headers=self.headers(),
            data={
                "num_chapters_read": readChapter,
            }
        )
        if not r:
            return False
        return True
#### MIGHT need this. useless for now
        # if result["chaptersRead"] <= readChapter: #Chapter saved in mangalist <= to chapter just read with tool
        #     pass #updating function
        # else:
        #     print("")
