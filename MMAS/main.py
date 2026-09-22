import sys
import os
import click

from pathlib import Path

from API.Mal.manga.msearchnsort import manageMal as MMal
from API.Mal.anime.asearchnsort import manageMal as AMAL

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

@click.group()
def cli():
    """Manga/Anime searcher and Cli tool integration"""
    pass

@cli.command(help="Search anime or manga by Title. Use --type to specify manga or anime (default: manga)")
@click.argument('title')
@click.argument ('mediatype',
                type =click.Choice(['manga','anime'], case_sensitive=False))
@click.option('--type', '-t',
                'aType',
                type=click.Choice(['sub','dub'], case_sensitive=False),
                default='sub',
                show_default=True,
                help="Audio track for anime (ignored for manga). ")

# @click.option('--jp', '-japanese',
#             type=click)
# Consideration is adding japanese manga. haven't found any source yet.

def search(title, mediatype, aType):
    """Search anime or manga by Title"""

    if not Path.exists("JsonIO"):
        os.mkdir("JsonIO")
    
    if mediatype.lower() == "manga":
        print(f"Searching for Manga titled {title}")
        MMal().searchMangaMatch(title)
    elif mediatype.lower() == "anime": 
        print(f"Searching for Anime titled {title} in {aType}")
        AMAL().searchAnimeMatch(title, aType)
    else :
        print("How did we get here? https://c.tenor.com/omyuVB-fnjMAAAAd/tenor.gif")

if __name__ == '__main__':

    cli()