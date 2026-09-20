import json
import subprocess
import time

from pathlib import Path

from API.Mal.requests import reqMal
from API.MD.requests import MangaDexAPI as reqMd
from API.Hianime.anicli import primeSession, searchAnime as hianimeSearch
from config import mpvPath, JsonIO

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


class ManageAnime(ManageMal):
    """"""
    def __repr__(self):
        return f"{type(self).__name__}(media={self.media!r})"

    MEDIA       = "anime"
    COUNT_KEY   = "episodesWatched"
    COUNT_FIELD = "num_episodes_watched"
    UNIT        = "Episode"


class ManageManga(ManageMal):

    def __repr__(self):
        return f"{type(self).__name__}(media={self.media!r})"

    MEDIA       = "manga"
    COUNT_KEY   = "chaptersRead"
    COUNT_FIELD = "num_chapters_read"
    UNIT        = "Chapter"




