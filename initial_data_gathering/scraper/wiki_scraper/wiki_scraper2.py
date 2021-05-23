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

REG = re.compile(r"[\/\"\\]")

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

artists = pd.read_csv("unique_artists_FINALISSIMISSIMO_2006_2021.csv", sep=";")
found = 0
not_found = 0

pairs = []

for artist in artists["artists_names"]:
    artist = REG.sub(" ", artist)
    pair = [artist, ""]
    try:
        page_title, page_link = wikiapi2.wiki_getter(WIKIAPI_SESSION, artist.strip())
        if not page_title:
            print(f"NOT FOUND artist: {artist}")
            not_found += 1
            continue
        with open(download_path + "/" + page_title + ".html", "w", encoding='utf-8') as fileh:
            fileh.write(get_html(WIKIPEDIA_SESSION, page_link))
            print(f"FOUND artist: {page_title}")
            found += 1
            pair[1] = page_title
    except:
        print(f"catched exception for {artist}")
        continue
    finally:
        pairs.append(pair)

WIKIAPI_SESSION.close()
WIKIPEDIA_SESSION.close()
pd.DataFrame(pairs, columns=["spotyname", "wikipagename_it"]).to_csv("wikipages_it.csv", sep=";", index=False)

print(f"total of {found} artists found and {not_found} not found")
