import os 
import shutil

from pathlib import Path
from cryptography.fernet import Fernet
from platformdirs import user_config_dir, user_data_dir

APPNAME    = "mmas"    #MangaMalAniSearch
APPAUTHOR = "Lucman00"

CONFIGDIR   = Path(user_config_dir(APPNAME,APPAUTHOR))
DATADIR     = Path(user_data_dir(APPNAME, APPAUTHOR))
CONFIGDIR.mkdir(parents=True, exist_ok=True)
DATADIR.mkdir(parents=True, exist_ok=True)

EKEYPATH    = CONFIGDIR / "fernet.key"
CIDPATH     = CONFIGDIR / "clientID" #might not even need this. who knows
TOKENPATH   = CONFIGDIR / "token.json"

def loadOrCreateEkey() -> Fernet:
    if EKEYPATH.exists():
        key = EKEYPATH.read_bytes().strip()
    else:
        key=Fernet.generate_key()
        EKEYPATH.write_bytes(key)
        try:
            os.chmod(EKEYPATH, 0o600)
        except OSError:
            pass #pov non unix system
    return Fernet(key)

EKEY = loadOrCreateEkey() #runs at config time. startup.

bakedCliId = "0dd424da750d115b174ffaeb75eeac74"

def getClientId() -> str:
    if CIDPATH.exists():
        return CIDPATH.read_text().strip()
    return bakedCliId


mangaFolder = str(DATADIR / "manga")
Path(mangaFolder).mkdir(parents=True, exist_ok=True)

mpvPath = shutil.which("mpv")
