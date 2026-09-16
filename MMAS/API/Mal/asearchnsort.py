from API.Mal.arequests import reqMal
from pathlib import Path
from API.Hianime.anicli import primeSession
from config import mpvPath

import subprocess
import json
import time

class manageMal:
    def __init__(self):
        self.mal = reqMal() 
    
    def getAllAnimeTitles(self):
    
        if Path("JsonIO/animeList.json").exists():
            with open("JsonIO/animeList.json", "r") as f:
                s = json.load(f)
                
                
            animeData = {}
            
            for i,x in enumerate(s["data"]):
                animeID = s["data"][i]["node"]["id"]
                animeTitles = s["data"][i]["node"]["alternative_titles"]
                animeStatus = s["data"][i]["node"]["my_list_status"]
                
                allTitles = []
                if animeTitles.get("en"):
                    allTitles.append(animeTitles["en"])
                if animeTitles.get("synonyms"):
                    allTitles.extend(animeTitles["synonyms"])
                episodesWatched = animeStatus.get("num_episodes_watched", 0)
                
                animeData[animeID] = {
                    "id": animeID,
                    "titles": allTitles,
                    "mainTitle": s["data"][i]["node"]["title"],
                    "episodesWatched": episodesWatched,
                    "fetchedAt": time.time()
                }
                
            
            
            
            with open ("JsonIO/aEnTitles.json", "w") as e:
                json.dump(animeData, e, indent=2)

            
        else: 
            reqMal().getAnimeList()
            self.getAllAnimeTitles()
            
    def searchAnime(self, query):
        if not Path("JsonIO/aEnTitles.json").exists() :
            self.getAllAnimeTitles()
            self.searchAnime(query)
        
        with open("JsonIO/aEnTitles.json", "r") as f:
            data = json.load(f)


        if data and time.time() - list(data.values())[0]["fetchedAt"] > 86400:
            print("data out of date, getting new")
            self.getAllAnimeTitles()
            with open("JsonIO/aEnTitles.json", "r") as f:
                data = json.load(f)
        results=[]

        for _, info in data.items():
            for title in info["titles"]:
                if query.lower() in title.lower():
                    results.append(info)
                    break

        return results

    def searchAnimeMatch(self, query, type:str = ""):


        results = self.searchAnime(query)
        if not results:
            print(f"No anime found for '{query}' in {type}")
            print("Check if anime is in your MAL list")
            return None
        print(f"Found Anime '{query}' in {type}")
        result = results[0]
        
        titles = result["titles"]
        watched = result["episodesWatched"]

        matched=False
        for title in titles:
            if title.lower() == query.lower().strip():
                matched = True
                break
        if matched:
            watchingEpisode = watched+1 #Assigns value that is the users next in line chapter to be read

            print(f"Loading {query}, Episode {watchingEpisode} ind {type}")


            


            while True:
                master, referer = primeSession(query,watchingEpisode,type)
                mpvProcess = subprocess.Popen([
                    mpvPath,
                    "--fs",
                    "--keep-open=no",
                    f"--http-header-fields=Referer: {referer}",
                    "--sid=auto",
                    "--slang=en,eng",
                    master,
                ])
                time.sleep(3)

                if mpvProcess is None:
                    print("Exiting..")
                    break
                while True:

                    if mpvProcess.poll() is not None:
                        break
                    time.sleep(2)

                response = input(f"Did you finish watching Episode: {watchingEpisode}? [y/n]").lower()

                if response == "y": #yes
                    ##update MAL
                    print("Updating MAL reading Status")
                    time.sleep(1)
                    if self.mal.updateMal(query, watchingEpisode ):
                        print("Updated List")
                    asknextchapter = input(f"Do you want to continue watching? (Next EP is {watchingEpisode+1}) [y/n]").lower()

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
                    print("Episode not finished. No changes saved. Exiting...")
                    time.sleep(1)
                    break
                else:
                    print("Invalid input. Exiting...")
                    time.sleep(1)
                    break


        else:
            print(f"Exact match not found for '{query}'. Available titles: {', '.join(titles[:3])}")
        
        