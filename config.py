from dotenv import load_dotenv
from cryptography.fernet import Fernet
from pathlib import Path

import os


load_dotenv(encoding='utf-8-sig')
MDKEY = os.getenv("MDKEY")
EKEY = Fernet(os.getenv("ENCRYPTKEY").encode())
UNAME = os.getenv("USERNAME")
PASS = os.getenv("PASSWORD")
MDID = os.getenv("MDID")

url = os.getenv("URL")
auth = os.getenv("AUTHURL")

mangaFolder = Path.home() / "Projects" / "Documents" / "Manga"

if not mangaFolder.exists():
    mangaFolder.mkdir(parents=True)

mangaFolder = str(mangaFolder)

possiblePath = [
    Path.home() / "scoop" / "shims" / "mpv.exe",
    Path.home() / "scoop" / "apps" / "mpv" / "current" / "mpv.exe",
    Path.home() / "AppData" / "Local" / "Programs" / "mpv" / "mpv.exe",
    Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Links" / "mpv.exe",
    Path("C:/") / "Program Files" / "mpv" / "mpv.exe",
    Path("C:/") / "Program Files (x86)" / "mpv" / "mpv.exe",
    Path("C:/") / "tools" / "mpv" / "mpv.exe",
]

mpvPath = next((p for p in possiblePath if p.exists()), None)
if mpvPath is None:
    print("MPV  not found. Please Install")