import json
import requests
import os

from MDauth import isTokenValid
from config import url


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
    def getChapters(self, Chapter):
        with open("filteredList.json", "r") as f:
            data = json.load(f)
            ID = data[0]["id"]
        if isTokenValid():
            query = f"{self.base_url}/manga/{ID}/feed"
            print(query)
            r = requests.get(
                f"{self.base_url}/manga/{ID}/feed",
                params={
                    "translatedLanguage[]": ["en"],
                    "chapterNumber": Chapter
                }
            )
        chapters = r.json()
        print(chapters)
        #if chapters:
        #    chapter_id = chapters[0]["id"]
        
        #rd = requests.get(
        #    f"{self.base_url}/at-home/server/{chapter_id}.chapter.data"
        #)
        #print(rd)

    def simpleMangaId(self, query, rp):
        data = rp

        filtered = []
        for manga in data['data']:
            attrs = manga['attributes']
            has_english = (
                attrs.get('title', {}).get('en') or
                any(alt.get('en') for alt in attrs.get('altTitles', [])) or
                attrs.get('description', {}).get('en')
            )
            if has_english:
                simplified = {
                    "id": manga['id'],
                    "title": attrs.get('title', {}),
                    "altTitles": attrs.get('altTitles', []),
                    "lastChapter": attrs.get('lastChapter'),
                    "status": attrs.get('status'),
                    "availableTranslatedLanguages": attrs.get('availableTranslatedLanguages', [])
                }
                filtered.append(simplified)

        if filtered:
            etitles = [filtered[0]['title'].get('en')] + [alt.get('en') for alt in filtered[0]['altTitles'] if alt.get('en')]
            
            if query in etitles:
                filtered = [filtered[0]]

        with open("filteredList.json", "w") as f:
            json.dump(filtered, f, indent=2)
        
        
        
api = MangaDexAPI(lang="en")
query = "Spice and Wolf"
response = api.search_manga(query, 5)
print(response.status_code)
api.simpleMangaId(query, response.json())

api.getChapters(1)