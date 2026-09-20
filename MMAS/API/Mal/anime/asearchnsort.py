import json
import subprocess
import time
from pathlib import Path

from API.Mal.requests import reqMal
from API.Hianime.anicli import primeSession, searchAnime as hianimeSearch
from config import mpv_path, JsonIO


class ManageMal:
    ANIMELISTPATH=JsonIO / "animeList.json"
    ENTITLESPATH =JsonIO / "animeEnTitles.json"

    def __init__(self):
        self.mal = reqMal("anime") 
    
    def getAllAnimeTitles(self):
        if not self.ANIMELISTPATH.exists():
            self.mal.get_list()
        if not self.ANIMELISTPATH.exists():
            raise RuntimeError(f"{self.ANIMELISTPATH} was not created.")
    
        with open(self.ANIMELISTPATH, "r") as f:
            s = json.load(f)
            
            
        animeData = {}
        
        for entry in s["data"]:
            animeID     = entry["node"]["id"]
            animeTitles = entry["node"]["alternative_titles"]
            animeStatus = entry["node"]["my_list_status"]
            
            allTitles = []
            en          = animeTitles.get("en")
            synonyms    = animeTitles.get("synonyms")

            if en:
                allTitles.append(en)
            if synonyms:
                allTitles.extend(synonyms)
    
            episodesWatched = animeStatus.get("num_episodes_watched", 0)
            status          = animeStatus.get("status")
            
            animeData[animeID] = {
                "id":               animeID,
                "titles":           allTitles,
                "mainTitle":        entry["node"]["title"],
                "episodesWatched":  episodesWatched,
                "status":           status,
                "fetchedAt":        time.time()
            }
            
        
        
        
        with open (self.ENTITLESPATH, "w") as e:
            json.dump(animeData, e, indent=2)



    def searchAnime(self, query):
        if not self.ENTITLESPATH.exists():
            self.getAllAnimeTitles()
        if not self.ENTITLESPATH.exists():
            raise RuntimeError("english titles file missing and not created.")
        
        with open(self.ENTITLESPATH, "r") as f:
            data = json.load(f)


        if data:
            newest = max(v["fetchedAt"] for v in data.values())
            if time.time() - newest > 86400:
                print("data out of date, getting new")
                self.getAllAnimeTitles()
                with open(self.ENTITLESPATH, "r") as f:
                    data =json.load(f)

        results=[]

        for info in data.values():
            allTitles = info["titles"] + [info["mainTitle"]]
            if any(query.lower() in t.lower() for t in allTitles):
                results.append(info)
        if results:
            return results  

        print(f"{query} not found in your list.")
        answer = input("Continue search outside of your list? [y/n]: ").strip().lower()

        if answer == "y":
            remote = self.mal.look_up_entry(query)
            for info in remote.values():
                allTitles = info["titles"] + [info["mainTitle"]]
                if any(query.lower() in t.lower() for t in allTitles):
                    results.append(info)
            if results:
                return results
            return []

        if answer == "n":
            print("Okay, exiting")
            return []

        print("Unknown answer, exiting")
        return []
                
    def searchAnimeMatch(self, query, mode: str = ""):
        result = self.chooseFromMal(query)
        if result is None:
            print(f"Check if '{query}' is in your MAL list.")
            return

        malId       = result["id"]
        malTitle    = result["mainTitle"]
        watched     = result["episodesWatched"]
        watchingEpisode = watched + 1

        # Resolve the Hianime watch URL once, using the MAL-canonical title.
        watchUrl = self.resolveHianimeUrl(malTitle)
        print(f"Loading {malTitle}, Episode {watchingEpisode} in {mode}")

        while True:
            try:
                master, referer, subUrl = primeSession(
                    malTitle, watchingEpisode, mode, watchUrl=watchUrl
                )
            except Exception as e:
                print(f"Failed to prime session: {e}")
                break

            mpvArgs = [
                mpv_path, "--fs", "--keep-open=no",
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
            mpvProcess.wait()            

            response = input(f"Did you finish watching Episode {watchingEpisode}? [y/n]: ").strip().lower()

            if response == "y":
                print("Updating MAL status...")
                time.sleep(1)
                if self.mal.update_mal(malId, watchingEpisode):
                    print("Updated list.")
                askNext = input(
                    f"Continue with Episode {watchingEpisode + 1}? [y/n] "
                ).lower()
                if askNext == "y":
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
            print("No results")
            return None

        for i, info in enumerate(results, start=1):
            print(f"{i}. {info['mainTitle']} (watched: {info['episodesWatched']})")

        while True:
            raw = input(f"Pick a number (1-{len(results)}): ").strip()
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