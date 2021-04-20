from bs4 import BeautifulSoup
from tqdm import tqdm
from unidecode import unidecode
import requests

import logging

import csv
from datetime import date
import os

from typing import List

logging.basicConfig(format='%(levelname)s\t%(message)s',
                    filename="parsing.log",
                    filemode="w",
                    level=logging.INFO)

CHART_CODE = 18
VERBOSE = True
CHART_NAME = "italy_top_20"
URL = f"https://top40-charts.com/chart.php?cid={CHART_CODE}&date="
START_DATE = '2018-11-15'
END_DATE = '2021-04-01'
DOWNLOAD_DIR = "downloads"
FIELD_NAMES = ["rank", "title", "artist"]
global next_date


def get_html(url: str) -> BeautifulSoup:
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
    doc = requests.get(url)
    doc.raise_for_status()
    return BeautifulSoup(doc.text, 'html.parser')


def get_songs(soup: BeautifulSoup) -> List[List[str]]:
    """
    This function takes an html file and returns a list of lists containing rank, name and artist
    Parameters
    ----------
    soup : BeautifulSoup
    BeautifulSoup object that contains an html representing the charts of a given week
    Returns
    -------
    List[List[str]]
    """
    chart_songs = soup.find_all("tr", class_="latc_song")
    global next_date
    next_date = soup.find("a", string="Next")["href"][-10:]
    out = []
    for chart_song in chart_songs:
        order, _, chart_song, singer, *_ = chart_song.find_all(text=True)
        out.append([
            unidecode(order),
            unidecode(chart_song),
            unidecode(singer)
        ])
    return out


if __name__ == "__main__":
    # Create download folder if not present
    try:
        os.mkdir(DOWNLOAD_DIR + "/" + CHART_NAME)
    except FileExistsError:
        pass

    current_date = START_DATE
    end = date.fromisoformat(END_DATE)
    unique_songs = []

    # Parse from start date to end date
    # fromisoformat must stay here since in other parts of the script is used as a string
    while date.fromisoformat(current_date) <= end:
        chart_url = URL + current_date
        csv_filename = DOWNLOAD_DIR + "/" + CHART_NAME + "/" + current_date + "_" + CHART_NAME + ".csv"
        html = get_html(chart_url)  # download the html file
        try:
            data = get_songs(html)  # retrieve the songs on the html
        except TypeError:
            logging.warning(f"{current_date} not parsed")
            continue

        if VERBOSE:
            print(current_date)
        with open(csv_filename, "w", newline='', encoding='utf-8') as file_handler:
            # use semicolon as delimiter since different artist of the same song are separated by commas
            writer = csv.writer(file_handler, delimiter=';',
                                quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(FIELD_NAMES)
            for rank, song, artist in data:
                writer.writerow([rank, song, artist])

                # Create of all the unique songs in all the charts
                if artist + ";" + song not in unique_songs:
                    unique_songs.append(artist + ";" + song)

                if VERBOSE:
                    print(f"\t{song}\t{artist}")
        logging.info(f"Parsing {current_date}")

        current_date = next_date
    # ==================================================================================================================

    if VERBOSE:
        print("Now I'm saving all distinct songs")
    # Save unique songs in a file
    with open("unique_songs.txt", "w") as unique_file:
        unique_file.write("artists;song")
        for song in tqdm(unique_songs):
            unique_file.write("\n" + song)
