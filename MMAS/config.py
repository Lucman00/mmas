from dotenv import load_dotenv
from cryptography.fernet import Fernet
from pathlib import Path
import shutil

import os

BASE_DIR = Path(__file__).resolve().parent

tokenPath = BASE_DIR / "token.json"
env_path  = BASE_DIR / ".env"


load_dotenv(env_path, encoding='utf-8-sig')
EKEY = Fernet(os.getenv("ENCRYPTKEY").encode())
cid = os.getenv("MALID")
key = os.getenv("MALKEY")
reurl = "http://localhost:8080"

mangaFolder = Path.home() / "Projects" / "Documents" / "Manga"



if not mangaFolder.exists():
    mangaFolder.mkdir(parents=True)

mangaFolder = str(mangaFolder)

possiblePath = shutil.which("mpv")
if not possiblePath:
    print("mpv not found")
else:
    mpvPath = possiblePath