# MMAS — Manga/Anime CLI searcher and player

A command-line tool that plays anime and downloads/reads manga, syncing your
progress to MyAnimeList automatically.

## DISCLAIMER

This tool is provided for **educational and personal use only**.

- This software does **not host, store, upload, or distribute** any media content.
- All content is fetched from **third-party sources** that are publicly accessible on the internet.
- This tool functions similarly to a **web browser** — it automates requests to publicly available content and plays the result in a local media player (mpv).
- The developers and contributors of this project **do not endorse, condone, or encourage piracy** or any form of copyright infringement.
- **You are solely responsible** for how you use this software and for ensuring your use complies with all applicable laws in your jurisdiction.
- If you are a rights holder and believe content accessible through this tool infringes your rights, please contact the **actual hosting provider** of that content, not the maintainers of this tool.

By using this software, you acknowledge and accept these terms.

---

## Data Sources & Attribution

- **MangaDex API** — Manga metadata and chapters are provided by
  [MangaDex](https://mangadex.org). This project is not affiliated with
  MangaDex. Please support official releases and scanlation groups.
- **MyAnimeList API** — Anime metadata is provided by
  [MyAnimeList](https://myanimelist.net). This project is not affiliated
  with MAL.
- **Anime streaming** — Streams are resolved from publicly accessible
  third-party sources. This project does not host any video content.

---

## MangaDex Acceptable Usage Policy Compliance

This tool:

- Credits MangaDex and scanlation groups in its output.
- Is not monetized (no ads, no paid access, no paywalls).
- Accepts donations only (if applicable).
- Will honor takedown/removal requests from scanlation groups.

If you are a scanlation group and want your content excluded, open an issue.

---

## What it does

- Searches your MAL anime/manga list by title
- Plays anime episodes via mpv (sourced by a Hianime stream)
- Downloads and reads manga chapters via mpv (sourced from MangaDex)
- Updates your MAL progress after each episode/chapter  
- Can search MAL's catalog for titles not on your list yet  

## Requirements

- Python 3.11+
- [mpv](https://mpv.io/)  (see below)
- A MyAnimeList account
- (Playwright browsers — installed via `mmas setup browser`)
- [Pipx](https://pipx.pypa.io/latest/index.html) (see below)
  
### Installing pipx

- **Arch:**  `sudo pacman -S python-pipx`
- **Ubuntu/Debian:**  `sudo apt install pipx`
- **Fedora:**  `sudo dnf install pipx`

- **macOS:**  `brew install pipx`

- **Windows (Scoop):**  `scoop install pipx`
- **Windows (pip):**  `py -m pip install --user pipx`

After installing, run:

- **Linux/macOS:**  `pipx ensurepath`

- **Windows (PowerShell):**  `py -m pipx ensurepath`

Then restart your shell/PowerShell.

## Install the package

- `pipx install mmas`

## First-time setup

### 1. Install Playwright browsers

- **In Shell:** ``mmas setup browser``

### 2. Authorise/Login

- **``mmas login``**

-- // This opens the Browser to a MAL page to authorise. Once you click approve or allow,
this tool receives Tokens to be able to query your Anime / Manga List.
You may see this page again if you haven't used this tool in a **Month**.
This is because these tokens expire of course.

If the browser doesn't open, copy the URL printed in the terminal
into your browser manually.

### Installing mpv
- mmas can install mpv for you if you don't have it already

**In Shell**: ``mmas setup mpv``


### 3. Runtime

- Now the tool is ready to be used
**Usage examples:**
mmas search [--type [sub|dub]] <anime|manga> "title" 
mmas login [--nobrowser]
-- ``mmas search --type dub anime "Spice and wolf"  ``
-- ``mmas search manga "Spice and wolf"``

## Important notes

If the title isn't already on your MAL list, mmas ofers to search MAL's catalog and add the entry.

### Files

| What             | Windows               | Unix                  |
|------------------|-----------------------|-----------------------|
| Config           | `%LOCALAPPDATA%\mmas` | `~/.local/share/mmas` |
| Fernet key       | `...\mmas\fernet.key` | `.../mmas/fernet.key` |
| Encrypted tokens | `...\mmas\token.json` | `.../mmas/token.json` |
| Json cache       | `...\mmas\JsonIO`     | `.../mmas/JsonO`      |
| Manga pages      | `...\mmas\manga`      | `.../mmas/manga`      |

To reset everything, if necessary for any reason, delete the config directory.
To re-auth only, either run mmas login or delete `token.json`

## Troubleshooting

**Login Page keeps reloading, or "Port 8080 is alreadyd in use"**
Something on your machine is using port 8080, which mmas needs for the login callback.
Close it and retry.

**"auth failed: No tokens"**
Technically not possible as the tool automatically tries to authorize on run.
If it does appear: `mmas login`.

**"Hianime has no results"**
MAL uses romanji titles; Hianime often uses English ones. While i tried to deal with this
as best as possible, I am not perfect. If the search does fall through and you're 100% sure
it exists on both Hianime and MAL, try shorter query (i.e. "Spice" or "wolf") or an alternative title.
This will most likely give you broader results and an option to choose from them.
If it persists on one show specifically, try deleting the `hianime_urls.json` cache inside of JsonIO, see above.
And if despite all of this it still persists, please open an issue, I'm always open to suggestions and bug feedbacks.

**"Failed to prime session"**
The Hianime stream couldn't be resolved. The episode may not exist yet,
or the show was removed. Try a different episode.

**"No Manga downloaded"**
Mangadex has no English translation for that chapter.
This tool only supports English translated manga as Mangadex doesn't offer
any japanese originals and I haven't found a good source otherwise.
Again, open to suggestions, I'll take a look.

**mpv opens and closes immmediiately**
This is gonna be a mistake purely made by me.
This likely suggests mpv rejected an argument. If this happens,
please notify me immediately.

## How it works

- **Auth:** OAuth2 with PKCE against MAL. The client ID is bundled with
  mmas; no per-user setup required.
- **Tokens:** Encrypted with a Fernet key stored separately on disk.
- **Anime:** Streams scraped from Hianime, played via mpv with the correct
  Referer header.
- **Manga:** Pages downloaded from MangaDex, displayed as an image sequence
  in mpv.
- **Progress:** After each episode/chapter, mmas Patches your MAL entry.

## Known limitations

- Hianime and MangaDex are unofficial sources. If they change their HTML
  or endpoints, this tool breaks until the scraper is updated.
- Only English manga and sub/dub anime are supported.
- Title matching between MAL and Hianime is fuzzy; you may be prompted to
  pick the correct match once per series. The choice is cached.
- Auth uses a shared MAL API client. If MAL ever revokes it, all users are
  affected until mmas is updated.
- No offline mode.

## Development

git clone <https://github.com/Lucman00/mmas>
cd mmas
python -m venv .venv
.venv\Scripts\activate # or: source .venv/bin/activate
pip install -e .

## License

MIT License

Copyright (c) 2026 Luca Barthel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

### ADDITIONAL NOTICE

This license applies ONLY to the source code of this project. It does NOT
grant any rights to any third-party content, media, trademarks, or data
accessed through the software. The authors of this software do not host,
distribute, or claim ownership of any content retrieved by it.
