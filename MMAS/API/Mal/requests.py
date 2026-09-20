import requests
import json
import time

from API.Mal.auth import getAccessToken
from config import JsonIO
from pathlib import Path


class reqMal():


    def __init__(self, mediaType:str):
        if mediaType not in ("anime", "manga"):
            raise ValueError(
                f"I made a mistake in the code. Please report it. "
                f"Unknown mediaType: {mediaType!r}"
            )
        
        if mediaType == "manga":
                self.ceUnit, self.rwUnit = "chapters", "read"
        else:   self.ceUnit, self.rwUnit =  "episodes",  "watched" 

        self.media = mediaType
        self.url = "https://api.myanimelist.net/v2"

    def __repr__(self):
        return f"reqMal(media={self.media!r})"

    def authHeaders(self):
        return {"Authorization": f"Bearer {getAccessToken()}"}

    def getList(self):
        r=requests.get(f"{self.url}/users/@me/{self.media}list",
                    headers=self.authHeaders(),
                    params={
                        "sort":f"{self.media}_title",
                        "fields": "alternative_titles, my_list_status",
                        "limit": 200,
                    }
                )
        r.raise_for_status()

        with open(JsonIO / f"{self.media}List.json", "w") as f:
            json.dump(r.json(),f,indent=2)
        print(f"Successfully fetched {len(r.json()['data'])} {self.media} entries")
        return r.json()

    def lookupEntry(self, query):
        """Search up entries not found in User's active list """
        r = requests.get(
            f"{self.url}/{self.media}",
            headers=self.authHeaders(),
            params={
                "q": query,
                "limit": 10,
                "fields": "alternative_titles,my_list_status"
            },
        )
        r.raise_for_status()
        data = {}
        for entry in r.json()["data"]:
            node    = entry["node"]
            alt     = node.get("alternative_titles", {})
            status  = node.get("my_list_status") or {}
            dataID  = node["id"]

            allTitles = []
            if alt.get("en"):
                allTitles.append(alt["en"])
            allTitles.extend(alt.get("synonyms", []))

            countField  = f"num_{self.ceUnit}_{self.rwUnit}"
            count       = status.get(countField, 0)
            kind = ""
            if self.media == "anime":
                kind =  "episodesWatched"
            else: kind ="chaptersRead"

            data[dataID] = {
                "id":       dataID,
                "titles":   allTitles,
                "mainTitle":entry["node"]["title"],
                kind:       count,
                "status":   status.get("status"),
                "fetchedAt":time.time()
            }


        return data

    def updateMal(self, malId, progress):
        r = requests.patch(
            f"{self.url}/{self.media}/{malId}/my_list_status",
            headers=self.authHeaders(),
            data={
                f"num_{self.ceUnit}_{self.rwUnit}": progress,
            }
        )

        r.raise_for_status()
        return r.ok