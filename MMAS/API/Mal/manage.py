import json
import subprocess
import time
import re

from pathlib import Path

from API.Mal.requests import reqMal
from API.MD.requests import MangaDexAPI as reqMd
from API.Hianime.anicli import primeSession, searchAnime as hianimeSearch
from config import mpv_path, JsonIO, hianime_urls

class ManageMal:
    """This handles all the shared Logic"""

    def __repr__(self):
        media = getattr(self, "media", None)
        return f"{type(self).__name__}(media={media!r})"
    
    MEDIA:      str
    COUNT_FIELD:str
    UNIT:       str
    VERB:       str

    def __init__(self):
        if self.MEDIA is None:
            raise TypeError(f"{type(self).__name__} mnust define MEDIA")
        self.media  = self.MEDIA
        self.mal    = reqMal(self.MEDIA)
        self.list_path    = JsonIO / f"{self.media}List.json"
        self.titles_path  = JsonIO / f"{self.media}EnTitles.json"

    def get_all_en_titles(self):
        if not self.list_path.exists():
            self.mal.get_list()
        if not self.list_path.exists():
            raise RuntimeError(f"{self.list_path} was not created.")

        with open(self.list_path, "r") as f:
            data = json.load(f)

        new_data = {
            "media":        self.media,
            "fetched_at":   time.time(),
            "entries":      {},
        }

        for entry in data["data"]:
            node    = entry["node"]
            data_id = node["id"]
            titles  = node["alternative_titles"]
            status_dict  = node["my_list_status"]

            all_titles = []
            en      = titles.get("en")
            synonyms= titles.get("synonyms")

            if en:
                all_titles.append(en)
            if synonyms:
                all_titles.extend(synonyms)

            count   = status_dict.get(self.COUNT_FIELD, 0)
            status  = status_dict.get("status")

            new_data["entries"][data_id] = {
                "type":             self.media, #purely for readability
                "id":               data_id,
                "titles":           all_titles,
                "main_title":       node["title"],
                self.COUNT_FIELD:   count,
                "status":           status,
            }
        with open(self.titles_path, "w") as f:
            json.dump(new_data, f, indent=2)

    def search_data(self, query: str):
        if not self.titles_path.exists():
            self.get_all_en_titles()
        if not self.titles_path.exists():
            raise RuntimeError("English titles file missing and/or not created.")

        with open(self.titles_path,"r") as f:
            root = json.load(f)

        if root:
            time_stamp = root["fetched_at"]
            if time.time() - time_stamp > 86400:
                print("data out of date, getting new")
                self.get_all_en_titles()
                with open(self.titles_path, "r") as f:
                    root = json.load(f)

        entries = root["entries"]


        results = []

        for info in entries.values():
            all_titles = info["titles"] + [info["main_title"]]
            if any(query.lower() in t.lower() for t in all_titles):
                results.append(info)
        if results:
            return results

        print(f"{query} not found in your list.")
        answer = input("Continue search outside of your list? [y/n]: ").strip().lower()

        if answer == "y":
            remote = self.mal.look_up_entry(query)
            for info in remote.values():
                all_titles = info["titles"] + [info["main_title"]]
                if any(query.lower() in t.lower() for t in all_titles):
                    results.append(info)
            if results:
                return results
            return []

        if answer == "n":
            print("Okay, exiting")
            return []

        print("Unknown answer, exiting")
        return []

    def search_match(self, query, mode: str = ""):
        result = self.choose_mal(query)
        if result is None:
            print(f"Check if '{query}' is in your MAL list.")
            return

        mal_id      = result["id"]
        mal_title   = result["main_title"]
        number      = result[self.COUNT_FIELD] + 1

        while True:
            played = self._play(mal_title, mal_id, number, mode)
            if played is None:
                break

            response = input(
                f"Did you finish {self.UNIT.lower()} {number}? [y/n]: "
            ).strip().lower()

            if response == "y":
                print("Updating MAL status...")
                time.sleep(1)
                if self.mal.update_mal(mal_id, number):
                    print("Updated list.")
                else: 
                    print("MAL rejected the update")

                ask_next = input(
                    f"Continue with {self.UNIT} {number + 1}? [y/n] "
                ).strip().lower()
                if ask_next == "y":
                    number += 1
                    continue
                print("Goodbye.")
                break
            if response == "n":
                print(f"{self.UNIT} not finished. No changes saved.")
                break
            print("Invalid input.")
            break


    def choose_mal(self, query):
        results = self.search_data(query)
        if not results:
            print("No results")
            return None

        for i, info in enumerate(results, start=1):
            print(f"{i}. {info['main_title']} ({self.VERB}: {info[self.COUNT_FIELD]})")

        while True:
            raw = input(f"Pick a number (1-{len(results)}): ").strip()
            if not raw.isdigit():
                print("Not a number, try again.")
                continue
            choice = int(raw)

            if 1 <= choice <= len(results):
                return results[choice-1]
            print(f"Out of range. Pick between 1 and {len(results)}!")

class ManageAnime(ManageMal):
    """Subclass to handle any Anime related call"""

    MEDIA       = "anime"
    COUNT_FIELD = "num_episodes_watched"
    UNIT        = "Episode"
    VERB        = "Watched"

    def _play(self, mal_title:str, mal_id:int, number:int, mode:str = ""):
        watch_url = self.resolve_hianime_watch_url(mal_title, mal_id)
        print(f"Loading {mal_title}, Episode {number} in {mode}")

        try:
            master, referer, sub_url = primeSession(
                mal_title, number, mode, watchUrl=watch_url
            )
        except Exception as e:
            print(f"Failed to prime session: {e}")
            return None
        mpv_args = [
            mpv_path,
            "--fs",
            "--keep-open=no",
            f"--http-header-fields=Referer: {referer}",
            "--sid=auto",
            "--slang=en,eng,english",
            "--sub-file-paths=", 
            "--cache=yes",
            "--force-window=yes",
            "--demuxer-max-bytes=100MiB",
            master,
        ]
        if sub_url:
            mpv_args.append(f"--sub-file={sub_url}")
            mpv_args.append(f"--sid=1")

        mpv_process = subprocess.Popen(mpv_args)
        mpv_process.wait()
        return True


    def resolve_hianime_watch_url(self, mal_title:str, mal_id):
        """Search Hianime by the MAL title"""
        cache_path  = hianime_urls
        key         = str(mal_id)

        cache = {}

        if cache_path.exists():
            try:
                with open(cache_path) as f:
                    cache = json.load(f)
            except (json.JSONDecodeError, OSError):
                cache = {}
        if key in cache:
            return cache[key]


        hits = hianimeSearch(mal_title)
        if not hits:
            raise RuntimeError(f"Hianime has no results for {mal_title!r}")

        def _norm(s):
            return re.sub(r"[^a-z0-9]+", "", s.lower())

        target = _norm(mal_title)
        exact = [h for h in hits if _norm(h["title"]) == target]
        if len(exact) == 1:
            print(f"Using Hianime match: {exact[0]['title']}")
            url = exact[0]['url']

        elif len(hits) == 1:
            print(f"Using Hianime match: {hits[0]['title']}")
            url = hits[0]['url']
        else:
            for i, h in enumerate(hits, start=1):
                print(f"{i}. {h['title']}")

            while True: 
                raw = input(f"Pick a Hianime result (1-{len(hits)})").strip()
                if not raw.isdigit():
                    print("Not a number, try again.")
                    continue
                choice = int(raw)
                if 1 <= choice <= len(hits):
                    url = hits[choice - 1]["url"]
                    break
                print(f"Out of range, pick between 1 and {len(hits)}.")
        cache[key] = url
        with open(cache_path, "w") as f:
            json.dump(cache, f, indent=2)

        return url

class ManageManga(ManageMal):
    """Subclass to handle any MAnga related call"""

    MEDIA       = "manga"
    COUNT_FIELD = "num_chapters_read"
    UNIT        = "Chapter"
    VERB        = "Read"

    def __init__(self):
        super().__init__()
        self.md = reqMd()



    def __play(self, mal_title, mal_id, number, mode):
        print(f"Loading {mal_title}, Chapter {number}")
        proc =  self.md.load_manga(mal_title, number)

        if proc is None:
            return None

        proc.wait()
        return True
