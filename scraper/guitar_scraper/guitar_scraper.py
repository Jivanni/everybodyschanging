import re
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import time

import csv
from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm


chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('--headless')
chrome_options.add_argument('window-size=1920x1080')
chrome_options.add_argument("--user-data-dir=user");
driver = webdriver.Chrome(options=chrome_options)

DOWNLOAD_DIR = "downloads"
HTMLS = "lyrics"
TYPE = "title"
URL = f"https://www.ultimate-guitar.com/search.php"

REG = re.compile(r"[\/\"\\]")

try:
    download_path = os.path.join(DOWNLOAD_DIR, HTMLS)
    os.makedirs(download_path)
except FileExistsError:
    pass

def get_html(driver, url) -> BeautifulSoup:
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
    driver.get(url)
    driver.implicitly_wait(2)
    page_source = driver.page_source
    return BeautifulSoup(page_source, 'html.parser')

artists = pd.read_csv("unique_songs_v2.csv", sep=";")
found = 0
not_found = 0

pairs = []

PARAMS = {
    "search_type": TYPE,
    "value": "ciccio"
}

test = "https://tabs.ultimate-guitar.com/tab/olivia-rodrigo/good-4-u-chords-3705839"
pag = get_html(driver, test)

#_3uKbA
#_3rlxz
#GUITAR_SESSION.get("https://www.ultimate-guitar.com/search.php?search_type=title&value=ciccio").content