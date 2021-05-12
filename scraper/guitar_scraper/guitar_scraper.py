import re
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import time

DOWNLOAD_DIR = "downloads"
HTMLS = "lyrics"
TYPE = "title"
URL = f"https://www.ultimate-guitar.com/search.php"


GUITAR_SESSION = requests.Session()

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
    page_source = session.get(url=URL, params=PARAMS)
    time.sleep(2)

    return BeautifulSoup(page_source.content, 'html.parser')

artists = pd.read_csv("../wiki_scraper/unique_songs.csv", sep=";")
found = 0
not_found = 0

pairs = []

PARAMS = {
    "search_type": TYPE,
    "value": "ciccio"
}


pag = get_html(GUITAR_SESSION, "Ciccio")

#_3uKbA

session.get("https://www.ultimate-guitar.com/search.php?search_type=title&value=ciccio").content