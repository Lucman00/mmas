import json
import subprocess
import time

from pathlib import Path

from API.Mal.requests import reqMal
from API.MD.requests import MangaDexAPI as reqMd
#from API.Hianime.anicli import primeSession, searchAnime as hianimeSearch
from config import mpv_path, JsonIO

class ManageMal:
    """This handles all the shared Logic"""

    def __repr__(self):
        return f"{type(self).__name__}(media={self.media!r})"
    
    MEDIA:      str
    COUNT_KEY:  str
    COUNT_FIELD:str
    UNIT:       str


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

        newData = {}

        for entry in data["data"]:
            node    = entry["node"]
            dataID  = node["id"]
            alt     = node.get("alternative_titles", {})
            status  = node.get("my_list_status") or {}

        allTitles = []


class ManageAnime(ManageMal):
    """Subclass to handle any Anime related call"""
    def __repr__(self):
        return f"{type(self).__name__}(media={self.media!r})"

    MEDIA       = "anime"
    COUNT_KEY   = "episodesWatched"
    COUNT_FIELD = "num_episodes_watched"
    UNIT        = "Episode"


class ManageManga(ManageMal):
    """Subclass to handle any MAnga related call"""
    def __repr__(self):
        return f"{type(self).__name__}(media={self.media!r})"

    MEDIA       = "manga"
    COUNT_KEY   = "chaptersRead"
    COUNT_FIELD = "num_chapters_read"
    UNIT        = "Chapter"

