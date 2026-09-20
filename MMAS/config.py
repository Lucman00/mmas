import os 
import shutil

from pathlib import Path
from cryptography.fernet import Fernet
from platformdirs import user_config_dir, user_data_dir

APP_NAME    = "mmas"    #MangaMalAniSearch
APP_AUTHOR = "Lucman00"

CONFIG_DIR   = Path(user_config_dir(APP_NAME,APP_AUTHOR))
DATA_DIR     = Path(user_data_dir(APP_NAME, APP_AUTHOR))
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

EKEY_PATH    = CONFIG_DIR / "fernet.key"
CID_PATH     = CONFIG_DIR / "clientID" #might not even need this. who knows
TOKEN_PATH   = CONFIG_DIR / "token.json"

def _load_or_create_ekey() -> Fernet:
    if EKEY_PATH.exists():
        key = EKEY_PATH.read_bytes().strip()
    else:
        key=Fernet.generate_key()
        EKEY_PATH.write_bytes(key)
        try:
            os.chmod(EKEY_PATH, 0o600)
        except OSError:
            pass #pov non unix system
    return Fernet(key)

EKEY = _load_or_create_ekey() #runs at config time. startup.

bakedCliId = "1edac3e5b806a5eae0321f45ef7951e9"

def get_client_id() -> str:
    if CID_PATH.exists():
        return CID_PATH.read_text().strip()
    return bakedCliId


manga_folder = str(DATA_DIR / "manga")
Path(manga_folder).mkdir(parents=True, exist_ok=True)
JsonIO = Path(DATA_DIR) / "JsonIO"
Path(JsonIO).mkdir(parents=True, exist_ok=True)
hianime_urls = Path(DATA_DIR) / "JsonIO" / "hianime_urls.json"

mpv_path = shutil.which("mpv")
