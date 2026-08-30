from mrequests import reqMal
from pathlib import Path

import json
import time

class manageMal:
    def __init__(self):
        pass
    
    def getAllEnMangaTitles(self):
    
        if Path("mangaList.json").exists():
            with open("mangaList.json", "r") as f:
                s = json.load(f)
                
                
            mangaData = {}
            
            for i,x in enumerate(s["data"]):
                mangaID = s["data"][i]["node"]["id"]
                mangaTitles = s["data"][i]["node"]["alternative_titles"]
                
                allTitles = []
                if mangaTitles.get("en"):
                    allTitles.append(mangaTitles["en"])
                if mangaTitles.get("synonyms"):
                    allTitles.extend(mangaTitles["synonyms"])
                    
                mangaData[mangaID] = {
                    "id": mangaID,
                    "titles": allTitles,
                    "mainTitle": s["data"][i]["node"]["title"],
                    "fetchedAt": time.time()
                }
                
            
            
            
            with open ("enTitles.json", "w") as e:
                json.dump(mangaData, e, indent=2)

            
        else: 
            print(reqMal().getMangaList())
            self.getAllEnMangaTitles()
            
    def searchManga(self, query):
        with open("enTitles.json", "r") as f:
            data = json.load(f)
            
        results=[]
        for mangaID, info in data.items():
            for title in info["titles"]:
                if query.lower() in title.lower():
                    results.append(info)
                    break
        if results[0]["fetchedAt"] <= time.time() - 86400:
            self.getAllEnMangaTitles()
            self.searchManga()
        return results[0]["id"] 
        
    
print(manageMal().searchManga("Spice and wolf"))