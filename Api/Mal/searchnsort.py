from Api.Mal.mrequests import reqMal
from Api.MD.mrequests import MangaDexAPI as reqMd
from pathlib import Path

import json
import time

class manageMal:
    def __init__(self):
        pass
    
    def getAllEnMangaTitles(self):
    
        if Path("JsonOutputInput/mangaList.json").exists():
            with open("JsonOutputInput/mangaList.json", "r") as f:
                s = json.load(f)
                
                
            mangaData = {}
            
            for i,x in enumerate(s["data"]):
                mangaID = s["data"][i]["node"]["id"]
                mangaTitles = s["data"][i]["node"]["alternative_titles"]
                mangaStatus = s["data"][i]["node"]["my_list_status"]
                
                allTitles = []
                if mangaTitles.get("en"):
                    allTitles.append(mangaTitles["en"])
                if mangaTitles.get("synonyms"):
                    allTitles.extend(mangaTitles["synonyms"])
                chaptersRead = mangaStatus.get("num_chapters_read", 0)
                
                mangaData[mangaID] = {
                    "id": mangaID,
                    "titles": allTitles,
                    "mainTitle": s["data"][i]["node"]["title"],
                    "chaptersRead": chaptersRead,
                    "fetchedAt": time.time()
                }
                
            
            
            
            with open ("JsonOutputInput/enTitles.json", "w") as e:
                json.dump(mangaData, e, indent=2)

            
        else: 
            print(reqMal().getMangaList())
            self.getAllEnMangaTitles()
            
    def searchManga(self, query):
        if not Path("JsonOutputInput/enTitles.json").exists() :
            self.getAllEnMangaTitles()
            self.searchManga(query)
        
        with open("JsonOutputInput/enTitles.json", "r") as f:
            data = json.load(f)
        if data and time.time() - list(data.values())[0]["fetchedAt"] > 86400:
            self.getAllEnMangaTitles()
            with open("JsonOutputInput/enTitles.json", "r") as f:
                data = json.load(f)
            
        results=[]
        for mangaID, info in data.items():
            for title in info["titles"]:
                if query.lower() in title.lower():
                    results.append(info)
                    break

    def searchMangaMatch(self, query):
        results = self.searchManga(query)
        if not results:
            print(f"No manga found for '{query}'")
            return None
        result = results[0]
        
        titles = result["titles"]
        read = result["chaptersRead"][0]
        
        if query in titles:
            print(f"Loading {query}, starting from chapter {read + 1}")
            md = reqMd()
            md.loadManga(query,read)
        else:
            print(f"Exact match not found for '{query}'. Closest: {titles[0] if titles else 'None'}")
        
        