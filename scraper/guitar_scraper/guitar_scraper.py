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
chrome_options.add_argument('--headless')
chrome_options.add_argument("--user-data-dir=user");
driver = webdriver.Chrome(options=chrome_options)

DOWNLOAD_DIR = "downloads"
HTMLS = "lyrics"
TYPE = "title"
ENDPOINT = f"https://www.ultimate-guitar.com/search.php"

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
    text = driver.find_element_by_xpath("//code/pre").get_attribute('innerHTML')
    return BeautifulSoup(text, 'html.parser')

def getnotes(soup):
    notes = pag.findAll(style="color: rgb(0, 0, 0);")
    return str([note.text.strip() for note in notes])

artists = pd.read_csv("unique_songs_v2.csv", sep=";")
found = 0
not_found = 0

pairs = []

html_reg_repl = re.compile(r"\s")

def search(driver, artist_song):
    artist_song = html_reg_repl.sub("%20", artist_song)
    print(artist_song)
    query_string = f"?search_type=title&value={artist_song}"
    driver.get(ENDPOINT + query_string)
    driver.implicitly_wait(2)
    return BeautifulSoup(driver.page_source, 'html.parser')



#test = "https://tabs.ultimate-guitar.com/tab/ed-sheeran/perfect-chords-1956589"
#pag = get_html(driver, test)
#print(getnotes(pag))
#driver.close()
