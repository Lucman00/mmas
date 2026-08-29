import json
import requests
import os
import time

from MDauth import isTokenValid
from config import url, mangaFolder


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
    def getChapters(self, offset):
        with open("filteredList.json", "r") as f:
            data = json.load(f)
            ID = data[0]["id"]
        if isTokenValid():
            query = f"{self.base_url}/manga/{ID}/feed"
            r = requests.get(
                f"{self.base_url}/manga/{ID}/feed",
                params={
                    "translatedLanguage[]": ["en"],
                    "order[chapter]": "asc",
                    "limit": 1,
                    "offset": offset
                    
                }
            )
            chapters = r.json()
        if chapters:
            chapter_id = chapters ["data"][0]["id"]
        else: print("x")
        
        rd = requests.get(
            f"{self.base_url}/at-home/server/{chapter_id}"
        )
        rd.raise_for_status
        
        data= rd.json()
        baseUrl = data["baseUrl"]
        hash = data["chapter"]["hash"]
        fileNames = data["chapter"]["data"]
        
        folder = os.path.join(mangaFolder, f'chapter_{chapter_id[:8]}')
        os.makedirs(folder, exist_ok=True)

        start_time = time.time()
        
        for i, fileName in enumerate(fileNames, 1):
            url = f"{baseUrl}/data/{hash}/{fileName}"
            response = requests.get(url)
            response.raise_for_status()
            
            filePath = os.path.join(folder, f"page_{i}.jpg")
            with open(filePath, "wb") as f:
                f.write(response.content)
                
        elapsed = time.time() - start_time
        print(f"Downloaded pages in {elapsed:.2f} seconds")
    
        return folder
        

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
readchapter = 2
#later something like chapter = [malapisum]+1

response = api.search_manga(query, 5)


print(response.status_code)
api.simpleMangaId(query, response.json())

api.getChapters(readchapter)