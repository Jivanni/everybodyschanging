import re
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import wikiapi

DOWNLOAD_DIR = "downloads"
HTMLS = "artist_pages"

try:
    download_path = os.path.join(DOWNLOAD_DIR, HTMLS)
    os.makedirs(download_path)
except FileExistsError:
    pass
LANG = "it"
WIKI_URL = f"https://{LANG}.wikipedia.org/wiki/"

artists = pd.read_csv("unique_songs.csv", sep=";")
out = []
for auths in artists["artists"]:
    artists_split = re.split(r"feat.|,|&|/", auths)
    for artist in artists_split:
        page = wikiapi.wiki_getter(artist.strip())
        if not page:
            print(f"artist page of {artist} not found")
            continue
        with open(download_path+"/"+page.title+".html", "w", encoding='utf-8') as fileh:
            fileh.write(page.html())
            print(f"getting page of {page.title}")

