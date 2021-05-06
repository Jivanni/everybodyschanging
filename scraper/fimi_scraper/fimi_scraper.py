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
START_DATE = 2007
END_DATE = 2020
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
        #finds the div elements containing tag and publisher, publisher might be empty
        tag_publisher = chart_song.find("td", class_="c3").find_all("div")
        #finds the div element contaning the song title
        song_title = chart_song.find("div", class_= "chart-section-element-title").get_text().strip()
        # finds the div element contaning the artist name
        artist_name = chart_song.find("div", class_="chart-section-element-author").get_text().strip()
        # gets the tag from tag_publisher
        tag = tag_publisher[0].get_text().strip()
        # gets the publisher from tag_publisher
        publisher = tag_publisher[1].get_text().strip()
        # finds the td element contaning the current rank of the song
        curr_rank = chart_song.find("td", class_="c4").get_text().strip()
        # finds the td element contaning the previous rank of the song
        prev_rank = chart_song.find("td", class_="c5").get_text().strip()
        #finds the td element containing how low the song has been on the chart
        n_weeks = chart_song.find("td", class_="c6").get_text().strip()

        out.append([
            unidecode(curr_rank),
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
                logging.warning(f"week {week} missing")
                week += 1
                continue
            if VERBOSE:
                print(current_date)

            with open(csv_filename, "w", newline='', encoding='utf-8') as file_handler:
                # use semicolon as delimiter since different artist of the same song are separated by commas
                writer = csv.writer(file_handler, delimiter=';',
                                    quotechar='"', quoting=csv.QUOTE_ALL)
                writer.writerow(FIELD_NAMES)
                for curr_rank, song_title, artist_name, tag, publisher, prev_rank, n_weeks in songs_data:
                    writer.writerow([curr_rank, song_title, artist_name, tag, publisher, prev_rank, n_weeks])

                    # Create of all the unique songs in all the charts
                    entry = f'"{artist_name}";"{song_title}"'
                    if entry not in unique_songs:
                        unique_songs.append(entry)

                    if VERBOSE:
                        print(f"\t{song_title}\t{artist_name}")
            logging.info(f"Parsing {current_date}")

            week += 1
        logging.warning(f"end of year {year}")
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
