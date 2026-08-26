from MDauth import isTokenValid
from config import url
import requests

class MangaDexAPI:
    def __init__(self, lang="en"):
        self.base_url = url
        self.lang = lang
    

    def search_manga(self, query):
        if isTokenValid():
            r = requests.get(
                f"{self.base_url}/manga",
                params={"title": query}
            )
            return r
        
api = MangaDexAPI(lang="en")
response = api.search_manga("Look Back ")
print(response.status_code)
print(response.json())