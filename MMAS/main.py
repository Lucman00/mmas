import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import click

from pathlib import Path
from API.Mal.searchnsort import manageMal as Mal

@click.group()
def cli():
    """Manga/Anime searcher and Cli tool integration"""
    pass

@cli.command(help="Search anime or manga by Title. Use --type to specify manga or anime (default: manga)")
@click.argument('title')
@click.argument ('mediatype',
                type =click.Choice(['manga','anime'], case_sensitive=False))
# @click.option('--jp', '-japanese',
#             type=click)


def search(title, mediatype):
    """Search anime or manga by Title"""

    if not Path.exists("JsonIO"):
        os.mkdir("JsonIO")
    
    if mediatype.lower() == "manga":
        print(f"Searching for Manga titled {title}")
        Mal().searchMangaMatch(title)
    elif mediatype.lower() == "anime": 
        print("Not implemented yet")
    else :
        print("How did we get here? https://c.tenor.com/omyuVB-fnjMAAAAd/tenor.gif")

if __name__ == '__main__':

    cli()