import requests
import re
import base64
import json

from playwright.sync_api import sync_playwright as spw
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin, unquote


OBF_KEY = b'otaku-embed-v1'

def _xor_bytes(data: bytes) -> bytes:
    return bytes(b ^ OBF_KEY[i % len(OBF_KEY)] for i, b in enumerate(data))

def deobfuscate(blob: str) -> dict:
    raw = base64.b64decode(unquote(blob))
    return json.loads(_xor_bytes(raw).decode('utf-8'))

class EpisodeUnavailableError(ValueError):
    """MAL asked for an episode hianime doesn't have."""
BASE = "https://hianime.at"
SEARCH_URL = BASE + "/search?keyword={}"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:155.0) "
    "Gecko/20100101 Firefox/155.0")

session = requests.Session()
session.headers.update({
    "User-Agent": UA,
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://hianime.at/",
})

def searchAnime(query: str) -> list:
    url = SEARCH_URL.format(quote(query))
    response = session.get(url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for item in soup.select(".film_list-wrap .flw-item, .film_list-wrap .film-poster-ahref"):
        link = item.select_one("a[href]")
        title = item.select_one(".film-name, .dynamic-name, [title]")
        if not link:
            continue

        href = urljoin(BASE, link.get("href"))
        name = (
            title.get("title")
            if title and title.get("title")
            else title.get_text(" ", strip=True) if title else href
        )

        results.append({
            "title": name,
            "url": href
        })
    return results

def chooseAnime(query:str) -> str:

    results = searchAnime(query)

    if not results:
        raise RuntimeError(f"no results for {query!r}")

    for index, anime in enumerate(results, start=1):
        print(f"{index}. {anime['title']}")

    while True:
        raw = input(f"Pick a number (1-{len(results)}): ").strip()
        if not raw.isdigit():
            print("Not a number, try again")
            continue
        choice = int(raw)
        if 1 <= choice <= len(results):
            return results[choice - 1]["url"]
        print(f"Out of range, pick between 1 and {len(results)}.")

def getAnimeId(watchUrl):

    m = re.search(r"-(\d+)(?:\?|$)", watchUrl)
    if not m:
        raise ValueError(f"no anime id in {watchUrl!r}")
    
    return int(m.group(1))

def getEpisodes(watchUrl: str) -> list:
    aId = getAnimeId(watchUrl)
    r = session.get(f"{BASE}/api/theme/episode/list/{aId}",
                    headers={"Referer": BASE + "/"})
    r.raise_for_status()

    data = r.json()

    if not data.get("status"):
        raise RuntimeError(f"episode list returned status=false: {data}")

    soup = BeautifulSoup(data["html"], "html.parser")
    episodes =[]
    for a in soup.select("a.ssl-item.ep-item"):
        episodes.append({
            "number":   int(a["data-number"]),
            "id":       int(a["data-id"]),
            "url":      urljoin(BASE,a["href"]),
        })
    return episodes

def pickServer(html: str, serverName: str = "ZokoAnime", kind: str = "sub") -> str:
    soup = BeautifulSoup(html, "html.parser")
    for item in soup.select(".server-item"):
        if item.get("data-type") != kind:
            continue
        if item.get("data-server-name", "").strip() != serverName:
                    continue
        raw = item.get("data-hash")
        if not raw:
            continue
        return base64.b64decode(raw).decode("utf-8")
    raise ValueError(f"server {serverName!r} ({kind}) not found")

def getServer(eId:int) -> str:

    r = session.get(
        "https://hianime.at/api/theme/episode/servers",
        params={"episodeId": eId},
        headers={"Referer": "https://hianime.at/"},
    )

    r.raise_for_status()
    data = r.json()
    if not data.get("status"):
        raise RuntimeError(f"servers endpoint returned status = false: {data}")
    return data["html"]

def getEnglishSub(embedUrl: str) -> str | None:
    r = session.get(embedUrl, headers={"Referer": BASE + "/"}, timeout=20)
    m = re.search(r'window\.__P\s*=\s*"([^"]+)"', r.text)
    if not m:
        return None
    config = deobfuscate(m.group(1))
    for s in config.get("subtitles", []):
        if s.get("label", "").strip().lower() == "english":
            return s["src"]
    return None

def getM3u8(embedUrl: str, tout:int = 30000) ->tuple  :
    master= {}
    referer = {}
    subUrl = getEnglishSub(embedUrl)

    with spw() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=UA)
        page = ctx.new_page()

        def onResp(resp):
            url = resp.url
            if "master.m3u8" in url and "master" not in master:
                master["master" ] = url
                try:
                    headers= resp.request.headers
                    if "referer" in headers:
                        referer["referer"] = headers["referer"]
                except Exception:
                    pass

        page.on("response", onResp)
        page.goto(embedUrl, wait_until="networkidle", timeout=tout)
        page.wait_for_timeout(3000)
        browser.close()

        if "master" not in master:
            raise RuntimeError("master.m3u8 not captured. Video player embed may have changed")
        return (master["master"], referer.get("referer", "https://megacloud.tv/"), subUrl)





        
def primeSession(query: str, ep: int,  type: str = "sub", watchUrl: str = None) -> tuple :
    if watchUrl is None:
        watchUrl = chooseAnime(query)

    episodes = getEpisodes(watchUrl)
    firstEp = episodes[0]['id']
    lastEp = episodes[-1]['number']
    if ep > lastEp:
        raise EpisodeUnavailableError(
            f"{ep} does not exist in Hianime. This is the case if:\n"
            "  1. You have finished the Anime — check the MAL episode counter.\n"
            "  2. The Anime is still airing and this episode hasn't released yet.\n"
            "  3. The episode exists but hianime hasn't uploaded it yet."
        )
    ep = ep-1
    
        
    embed = pickServer(getServer(firstEp+ep), "ZokoAnime", type)
    master, referer, subUrl = getM3u8(embed)

    return master, referer, subUrl
