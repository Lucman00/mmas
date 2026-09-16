from API.Mal.arequests import reqMal
from pathlib import Path
from API.Hianime.anicli import primeSession, searchAnime as hianimeSearch, chooseAnime
from config import mpvPath

import base64
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
    def searchAnimeMatch(self, query, type: str = ""):
        result = self.chooseFromMal(query)
        if result is None:
            print(f"Check if '{query}' is in your MAL list.")
            return

        malTitle = result["mainTitle"]
        watched = result["episodesWatched"]
        watchingEpisode = watched + 1

        # Resolve the Hianime watch URL once, using the MAL-canonical title.
        watchUrl = self.resolveHianimeUrl(malTitle)
        print(f"Loading {malTitle}, Episode {watchingEpisode} in {type}")

        while True:
            try:
                master, referer, subUrl = primeSession(
                    malTitle, watchingEpisode, type, watchUrl=watchUrl
                )
            except Exception as e:
                print(f"Failed to prime session: {e}")
                break

            mpvArgs = [
                mpvPath, "--fs", "--keep-open=no",
                f"--http-header-fields=Referer: {referer}",
                "--sid=auto", "--slang=en,eng,english",
                "--sub-file-paths=", "--cache=yes", "--force-window=yes",
                "--demuxer-max-bytes=100MiB",
                master,
            ]
            if subUrl:
                mpvArgs.append(f"--sub-file={subUrl}")
                mpvArgs.append("--sid=1")

            mpvProcess = subprocess.Popen(mpvArgs)
            time.sleep(3)

            while mpvProcess.poll() is None:
                time.sleep(2)

            response = input(f"Did you finish watching Episode {watchingEpisode}? [y/n] ").lower()

            if response == "y":
                print("Updating MAL status...")
                time.sleep(1)
                if self.mal.updateMal(malTitle, watchingEpisode):
                    print("Updated list.")
                asknext = input(
                    f"Continue with Episode {watchingEpisode + 1}? [y/n] "
                ).lower()
                if asknext == "y":
                    watchingEpisode += 1
                    continue
                print("Goodbye.")
                break

            elif response == "n":
                print("Episode not finished. No changes saved. Exiting...")
                break
            else:
                print("Invalid input. Exiting...")
                break

    def chooseFromMal(self,query):
        results = self.searchAnime(query)
        if not results:
            print(f"No anime found for '{query}' in your MAL list.")
            return None

        for i, info in enumerate(results, start=1):
            print(f"{i}. {info['mainTitle']} (watched: {info['episodesWatched']})")

        while True:
            raw = input(f"Pick a number (1-{len(results)}):").strip()
            if not raw.isdigit():
                print("Not a number, try again.")
                continue
            choice = int(raw)

            if 1 <= choice <= len(results):
                return results[choice - 1]
            print(f"Out of range. pick between 1 and {len(results)}.")

    def resolveHianimeUrl(self, malTitle: str) -> str:
        """Search Hianime by the MAL title; if multiple hits, let user pick."""
        hits = hianimeSearch(malTitle)
        if not hits:
            raise RuntimeError(f"Hianime has no results for {malTitle!r}")

        if len(hits) == 1:
            print(f"Using Hianime match: {hits[0]['title']}")
            return hits[0]["url"]

        for i, h in enumerate(hits, start=1):
            print(f"{i}. {h['title']}")

        while True:
            raw = input(f"Pick a Hianime result (1-{len(hits)}): ").strip()
            if not raw.isdigit():
                print("Not a number, try again.")
                continue
            choice = int(raw)
            if 1 <= choice <= len(hits):
                return hits[choice - 1]["url"]
            print(f"Out of range, pick between 1 and {len(hits)}.")