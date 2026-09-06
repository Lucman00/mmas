
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import click
from Api.Mal.searchnsort import manageMal as Mal

@click.group()
def cli():
    pass

@cli.command()
@click.argument('title')
def search(title):
    """Search for manga by title"""
    Mal().searchMangaMatch(title)

if __name__ == '__main__':
    cli()