import json

from MDauth import isTokenValid
from config import url
import requests

class MangaDexAPI:
    def __init__(self, lang="en"):
        self.base_url = url
        self.lang = lang
    

    def search_manga(self, query, limit):

        order = {
            "relevance": "desc",
        }
        final_order_query = {}

        for key,value in order.items():
            final_order_query[f"order[{key}]"] = value

        if isTokenValid():
            r = requests.get(
                f"{self.base_url}/manga",
                params={
                    **{
                        "title": query,
                        "limit": limit
                },
                **final_order_query,
            })
            return r
        
api = MangaDexAPI(lang="en")
query = "Witch hat Atelier"
response = api.search_manga( query,
                            5)
print(response.status_code)

etitle = next(
    (t["en"] for t in response.json()["data"][0]["attributes"]["altTitles"] if "en" in t), 
    "Unknown"
)

with open ("latestResponse.json", "w") as f:
    json.dump({
        "manga_data": response.json(),
        "english_title": etitle
    }, f, indent=2)
