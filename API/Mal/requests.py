import requests
import json
import time

from API.Mal.auth import get_access_token
from config import JsonIO
from pathlib import Path


class reqMal():


    def __init__(self, media_type:str):
        if media_type not in ("anime", "manga"):
            raise ValueError(
                f"I made a mistake in the code. Please report it. "
                f"Unknown mediaType: {media_type!r}"
            )
        
        if media_type == "manga":
                self.ce_unit, self.rw_unit = "chapters", "read"
        else:   self.ce_unit, self.rw_unit =  "episodes",  "watched" 

        self.media = media_type
        self.url = "https://api.myanimelist.net/v2"

    def __repr__(self):
        return f"reqMal(media={self.media!r})"

    def auth_headers(self):
        return {"Authorization": f"Bearer {get_access_token()}"}

    def get_list(self):
        r=requests.get(f"{self.url}/users/@me/{self.media}list",
                    headers=self.auth_headers(),
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

    def look_up_entry(self, query):
        """Search up entries not found in User's active list """
        r = requests.get(
            f"{self.url}/{self.media}",
            headers=self.auth_headers(),
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
            data_id = node["id"]

            all_titles = []
            if alt.get("en"):
                all_titles.append(alt["en"])
            all_titles.extend(alt.get("synonyms", []))

            count_field  = f"num_{self.ce_unit}_{self.rw_unit}"
            count       = status.get(count_field, 0)
            kind = ""
            if self.media == "anime":
                kind =  "episodesWatched"
            else: kind ="chaptersRead"

            data[data_id] = {
                "id":       data_id,
                "titles":   all_titles,
                "mainTitle":entry["node"]["title"],
                kind:       count,
                "status":   status.get("status"),
                "fetchedAt":time.time()
            }


        return data

    def update_mal(self, mal_id, progress):
        updated = f"num_{self.rw_unit}_{self.ce_unit}" if self.media == "anime" else f"num_{self.ce_unit}_{self.rw_unit}"
        field   = "watching" if self.media == "anime" else "reading"

        r = requests.patch(
            f"{self.url}/{self.media}/{mal_id}/my_list_status",
            headers=self.auth_headers(),
            data={
                updated: progress,
                "status": field,
            }
        )

        r.raise_for_status()
        return r.ok