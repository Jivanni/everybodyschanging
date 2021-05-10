import re
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import wikiapi2

DOWNLOAD_DIR = "downloads"
HTMLS = "artist_pages"
WIKIAPI_SESSION = requests.Session()
WIKIPEDIA_SESSION = requests.Session()

try:
    download_path = os.path.join(DOWNLOAD_DIR, HTMLS)
    os.makedirs(download_path)
except FileExistsError:
    pass

def get_html(session, url) -> BeautifulSoup:
    """
    This function retrieves an html file given an url
    Parameters
    ----------
    url : str
    url of the page to download

    Returns
    -------
    BeautifulSoup() object
    """
    doc = session.get(url)
    doc.raise_for_status()
    return doc.text

artists = pd.read_csv("unique_songs.csv", sep=";")

for auths in artists["artists"]:
    artists_split = re.split(r"feat.|,|&|/", auths)
    for artist in artists_split:
        page_title, page_link = wikiapi2.wiki_getter(WIKIAPI_SESSION, artist.strip())
        if not page_title:
            print(f"artist page of {artist} not found")
            continue
        with open(download_path + "/" + page_title + ".html", "w", encoding='utf-8') as fileh:
            fileh.write(get_html(WIKIPEDIA_SESSION, page_link))
            print(f"getting page of {page_title}")

