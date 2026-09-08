import json
import requests
import os
import time
import subprocess
import re
from config import mangaFolder, mpvPath
from pathlib import Path


class MangaDexAPI:
    def __init__(self, lang="en"):
        self.base_url = "https://api.mangadex.org"
        self.lang = lang

    def searchManga(self, title, limit):

        order = {
            "relevance": "desc",
        }
        final_order_query = {}

        for key,value in order.items():
            final_order_query[f"order[{key}]"] = value

        r = requests.get(
            f"{self.base_url}/manga",
            params={
                **{
                    "title": title,
                    "limit": limit
                },
                **final_order_query,
            })
        return r
    def getChapters(self, offset):
        with open("JsonIO/filteredList.json", "r") as f:
            data = json.load(f)
            ID = data[0]["id"]
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
    
        print(folder)
        return folder
        

    def simpleMangaId(self, title, rp):
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
            
            if title in etitles:
                filtered = [filtered[0]]

        with open("JsonIO/filteredList.json", "w") as f:
            json.dump(filtered, f, indent=2)
            
    def loadManga(self, title, chapter):
        response = self.searchManga(title, 5)
        print(self.simpleMangaId(title, response.json()))
        
        mangaPath = Path(self.getChapters(chapter))
        images = sorted([f for f in Path(mangaPath).iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png')],key=lambda x: int(re.search(r'\d+', x.stem).group()))
        return subprocess.run([mpvPath, "--fs", "--keep-open=no", "--image-display-duration=inf", *[str(img) for img in images]])
        
