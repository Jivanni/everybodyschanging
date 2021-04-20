from bs4 import BeautifulSoup
from tqdm import tqdm
from unidecode import unidecode
from selenium import webdriver

import logging

import csv
import os
import time

from typing import List

VERBOSE = True
START_DATE = 2016
END_DATE = 2017
CHART_NAME = "top_singoli"
DOWNLOAD_DIR = "downloads"


CHARTS_CODES = {
    "top_album" : 1,
    "compilation" : 2,
    "top_singoli" : 3,
    "dvd" : 4,
    "vinili" : 5
}
CHART_CODE = CHARTS_CODES[CHART_NAME]
URL = f"https://www.fimi.it/top-of-the-music/classifiche.kl#/charts/{CHART_CODE}"
FIELD_NAMES = ["rank", "title", "artist", "tag", "publisher", "prev_rank", "n_weeks"]


logging.basicConfig(format='%(levelname)s\t%(message)s',
                    filename="parsing.log",
                    filemode="w",
                    level=logging.INFO)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('window-size=1920x1080')
driver = webdriver.Chrome(options=chrome_options)

def get_html(url : str) -> BeautifulSoup:
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
    time.sleep(2)
    page_source=driver.page_source
    return BeautifulSoup(page_source, 'html.parser')

def get_songs(soup: BeautifulSoup) -> List[List[str]]:
    """
    This function takes an html file and returns a list of lists containing rank, name and artist, tag,
    publisher, previous rank, and number of weeks it has been in chart.
    Parameters
    ----------
    soup : BeautifulSoup
    BeautifulSoup object that contains an html representing the charts of a given week
    Returns
    -------
    List[List[str]]
    """
    chart_songs = soup.select(".tab-pane.active tbody tr")
    out = []
    for chart_song in chart_songs:
        song_title, artist_name, tag, publisher, curr_position, prev_rank, n_weeks = chart_song.find_all(text=True)
        out.append([
            unidecode(curr_position),
            unidecode(song_title.lower()),
            unidecode(artist_name.lower()),
            unidecode(tag.lower()),
            unidecode(publisher.lower()),
            unidecode(prev_rank),
            unidecode(n_weeks)
        ])
    return out

if __name__ == "__main__":
    # Create download folder if not present
    try:
        os.mkdir(DOWNLOAD_DIR + "/" + CHART_NAME)
    except FileExistsError:
        pass

    unique_songs = []

    year = START_DATE

    while year <= END_DATE:
        week = 1
        while week <= 52:
            current_date = f"/{year}/{week}"
            chart_url = URL + current_date
            csv_filename = DOWNLOAD_DIR + "/" + CHART_NAME + "/" + f"{year}-{week}" + "_" + CHART_NAME + ".csv"
            soup = get_html(chart_url)
            songs_data = get_songs(soup)
            if not songs_data:
                logging.warning(f"end of year {year}")
                break
            if VERBOSE:
                print(current_date)

            with open(csv_filename, "w", newline='', encoding='utf-8') as file_handler:
                # use semicolon as delimiter since different artist of the same song are separated by commas
                writer = csv.writer(file_handler, delimiter=';',
                                    quotechar='"', quoting=csv.QUOTE_ALL)
                writer.writerow(FIELD_NAMES)
                for curr_position, song_title, artist_name, tag, publisher, prev_rank, n_weeks in songs_data:
                    writer.writerow([curr_position, song_title, artist_name, tag, publisher, prev_rank, n_weeks])

                    # Create of all the unique songs in all the charts
                    if artist_name + ";" + song_title not in unique_songs:
                        unique_songs.append(artist_name + ";" + song_title)

                    if VERBOSE:
                        print(f"\t{song_title}\t{artist_name}")
            logging.info(f"Parsing {current_date}")

            week += 1
        year += 1

    driver.quit()
        # ==================================================================================================================

    if VERBOSE:
        print("Now I'm saving all distinct songs")
    # Save unique songs in a file
    with open("unique_songs.csv", "w") as unique_file:
        unique_file.write("artists;song")
        for song in tqdm(unique_songs):
            unique_file.write("\n" + song)
