import sys
import os
import click
import subprocess

from pathlib import Path
from mpvsetup import setup_mpv
from API.Mal.manage import ManageAnime as MA
from API.Mal.manage import ManageManga as MM

@click.group()
def cli():
    """Manga/Anime searcher and Cli tool integration"""
    pass

@cli.command(help="Search anime or manga by Title. Use --type (-t) to decide the Audio track. This only applies to Anime",
            epilog='\b\nExample:\n\n  mmas search anime Spice and Wolf')
@click.argument ('mediatype',
                type =click.Choice(['manga','anime'],
                case_sensitive=False))
@click.option('--type', '-t',
                'audio',
                type=click.Choice(['sub','dub'], case_sensitive=False),
                default='sub',
                show_default=True,
                help="Audio track for anime (ignored for manga). ")
@click.argument('title', nargs=-1, required=True)


# @click.option('--jp', '-japanese',
#             type=click)
# Consideration is adding japanese manga. haven't found any source yet.

def search(title, mediatype, audio):
    """Search anime or manga by Title"""

    title = " ".join(title)
    if mediatype.lower() == "manga":
        print(f"Searching for Manga titled {title}")
        MM().search_match(title)
    elif mediatype.lower() == "anime": 
        print(f"Searching for Anime titled {title} in {audio}")
        MA().search_match(title, audio)
    else :
        print("How did we get here? https://c.tenor.com/omyuVB-fnjMAAAAd/tenor.gif")


@cli.command()
@click.option("--nobrowser", "-N", is_flag=True, help="Print URL and paste code manually")
def login(nobrowser):
    """Authenticate with MAL (runs automatically on first use)"""
    from API.Mal.auth import run_oauth_flow
    run_oauth_flow(nobrowser)
    click.echo("Authenticated")

@cli.command()
@click.argument('component', 
                type=click.Choice(['Browser','MPV'], case_sensitive=False))
def setup(component):
    if component == "Browsers":
        print("Downloading Playwright browsers (this may take a few minutes)...")
        try:
            subprocess.check_call([sys.executable, "-m", "playwright", "install"])
            print("Playwright browsers installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install Playwright browsers: {e}")
            print("This tool needs Playwright browsers. You can retry manually with: playwright install")
            sys.exit(1)
    elif component == "MPV":
        if not setup_mpv():
            sys.exit(1)

if __name__ == '__main__':
    cli()