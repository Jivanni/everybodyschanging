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
QUERY_PARAMS = "?search_type=title&value="

REG = re.compile(r"[\/\"\\]")

try:
    download_path = os.path.join(DOWNLOAD_DIR, HTMLS)
    os.makedirs(download_path)
except FileExistsError:
    pass

def get_page(driver, url) -> BeautifulSoup:
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
    return driver

def getnotes(driver):
    body = driver.find_element_by_tag_name('body')
    text = body.find_element_by_xpath("//code/pre").get_attribute('innerHTML')
    soup = BeautifulSoup(text, 'html.parser')
    notes = soup.findAll(style="color: rgb(0, 0, 0);")
    return str([note.text.strip() for note in notes])

def search_song(driver, artist_and_song):
    artist_and_song = html_reg_repl.sub("%20", artist_and_song)
    print(artist_and_song)
    query_string = ENDPOINT + QUERY_PARAMS + artist_and_song
    get_page(driver, query_string)
    return driver.find_element_by_tag_name('body')

def evaulate_query(body):
    tabs = body.find_elements_by_xpath("//article/div/div[//a]")
    parsed = [BeautifulSoup(tab.text, "html.parser") for tab in tabs]
    for i in parsed:
        spans = i.findAll("span")
        for span in spans:
            if span.has_attr('data-tip'):
                print(i.text)
    return [BeautifulSoup(tab.text, "html.parser") for tab in tabs]


#/html/body//article/div//header//a
#divs with a links : //article/div/div[//a]


artists = pd.read_csv("unique_songs_with_feats_4.csv", sep=";")
found = 0
not_found = 0

pairs = []

html_reg_repl = re.compile(r"\s")




test = "https://tabs.ultimate-guitar.com/tab/ed-sheeran/perfect-chords-1956589"
pag = search_song(driver, "wish you were here")
tabs = evaulate_query(pag)

#driver.close()
