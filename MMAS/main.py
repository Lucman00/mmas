import sys
import os
import click

from pathlib import Path

from API.Mal.manage import ManageAnime as MA
from API.Mal.manage import ManageManga as MM

@click.group()
def cli():
    """Manga/Anime searcher and Cli tool integration"""
    pass

@cli.command(help="Search anime or manga by Title. Use --type (-t) to decide the Audio track. This only applies to Anime")
@click.argument('title')
@click.argument ('mediatype',
                type =click.Choice(['manga','anime'],
                case_sensitive=False))
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

    
    if mediatype.lower() == "manga":
        print(f"Searching for Manga titled {title}")
        MM().search_match(title)
    elif mediatype.lower() == "anime": 
        print(f"Searching for Anime titled {title} in {aType}")
        MA().search_match(title, aType)
    else :
        print("How did we get here? https://c.tenor.com/omyuVB-fnjMAAAAd/tenor.gif")


@cli.command()
@click.option("--nobrowser", "-N", is_flag=True, help="Print URL and paste code manually")
def login(nobrowser):
    """Authenticate with MAL (runs automatically on first use)"""
    from API.Mal.auth import run_oauth_flow
    run_oauth_flow(nobrowser)
    click.echo("Authenticated")

if __name__ == '__main__':
    cli()