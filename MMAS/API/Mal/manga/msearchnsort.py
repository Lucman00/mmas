from API.Mal.manga.mrequests import reqMal
from API.MD.mrequests import MangaDexAPI as reqMd
from pathlib import Path

import json
import time

class manageMal:
    def __init__(self):
        self.md = reqMd()
        self.mal = reqMal() 
    
    def getAllEnMangaTitles(self):
    
        if Path("JsonIO/mangaList.json").exists():
            with open("JsonIO/mangaList.json", "r") as f:
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
                
            
            
            
            with open ("JsonIO/enTitles.json", "w") as e:
                json.dump(mangaData, e, indent=2)

            
        else: 
            reqMal().getMangaList()
            self.getAllEnMangaTitles()
            
    def searchManga(self, query):
        if not Path("JsonIO/enTitles.json").exists() :
            self.getAllEnMangaTitles()
            self.searchManga(query)
        
        with open("JsonIO/enTitles.json", "r") as f:
            data = json.load(f)


        if data and time.time() - list(data.values())[0]["fetchedAt"] > 86400:
            print("data out of date, getting new")
            self.getAllEnMangaTitles()
            with open("JsonIO/enTitles.json", "r") as f:
                data = json.load(f)
        results=[]

        for _, info in data.items():
            for title in info["titles"]:
                if query.lower() in title.lower():
                    results.append(info)
                    break

        return results

    def searchMangaMatch(self, query):


        results = self.searchManga(query)
        if not results:
            print(f"No manga found for '{query}'")
            return None
        print(f"Found Manga titled {query}")
        result = results[0]
        
        titles = result["titles"]
        read = result["chaptersRead"]

        matched=False
        for title in titles:
            if title.lower() == query.lower().strip():
                matched = True
                break
        if matched:
            readingChapter = read+1 #Assigns value that is the users next in line chapter to be read

            print(f"Loading {query}, starting from chapter {readingChapter}")


            


            while True:
                mpvProcess = self.md.loadManga(query,readingChapter) #downloads the chapter and loads up mpv with images 
                time.sleep(3)

                if mpvProcess is None:
                    print("Exiting..")
                    break
                while True:

                    if mpvProcess.poll() is not None:
                        break
                    time.sleep(2)

                response = input(f"Did you finish reading chapter {readingChapter}? [y/n]").lower()

                if response == "y": #yes
                    ##update MAL
                    print("Updating MAL reading Status")
                    time.sleep(1)
                    if self.mal.updateMal(query, readingChapter):
                        print("Updated List")
                    asknextchapter = input(f"Do you want to continue reading? (Next chapter is {readingChapter+1}) [y/n]").lower()

                    if asknextchapter == "y": #yes²
                        readingChapter += 1
                        continue
                    else:
                        print("Goodbye.")
                        time.sleep(0.5)
                        print("Exiting...")
                        time.sleep(1)
                        break

                        


                elif response == "n":
                    print("Chapter not finished. No changes saved. Exiting...")
                    time.sleep(1)
                    break
                else:
                    print("Invalid input. Exiting...")
                    time.sleep(1)
                    break


        else:
            print(f"Exact match not found for '{query}'. Available titles: {', '.join(titles[:3])}")
        
        