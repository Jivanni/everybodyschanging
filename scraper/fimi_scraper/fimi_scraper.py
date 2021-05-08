import csv
import logging
import os
import time
import re
from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm
from unidecode import unidecode

VERBOSE = True
START_DATE = 2000
END_DATE = 2020
CHART_NAME = "top_singoli"
DOWNLOAD_DIR = "./downloads"

CHARTS_CODES = {
    "top_album": 1,
    "compilation": 2,
    "top_singoli": 3,
    "dvd": 4,
    "vinili": 5
}
CHART_CODE = CHARTS_CODES[CHART_NAME]
FIMI_URL = f"https://www.fimi.it/top-of-the-music/classifiche.kl#/charts/{CHART_CODE}"
FIELD_NAMES = ["rank", "title", "artist",
               "tag", "publisher", "prev_rank", "n_weeks", "date"]

logging.basicConfig(format='%(levelname)s\t%(message)s',
                    filename="parsing.log",
                    filemode="w",
                    level=logging.INFO)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('window-size=1920x1080')
driver = webdriver.Chrome(options=chrome_options)


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
    driver.get(url)
    time.sleep(2)
    page_source = driver.page_source
    return BeautifulSoup(page_source, 'html.parser')


def get_songs(bs_obj: BeautifulSoup) -> List[List[str]]:
    """
    This function takes an html file and returns a list of lists containing
    rank, name and artist, tag, publisher, previous rank, and number of weeks
    it has been in chart.
    Parameters
    ----------
    bs_obj : BeautifulSoup
    BeautifulSoup object that contains an html representing the charts
    of a given week
    Returns
    -------
    List[List[str]]
    """
    chart_songs = bs_obj.select(".tab-pane.active tbody tr")
    date = bs_obj.find(class_="chart-section-header-subtitle")
    if not date:
        return []

    date = date.get_text()
    date_match = re.findall(r"\d\d.\d\d.\d\d\d\d", date)[-1]
    out = []
    for chart_song in chart_songs:
        # finds the div elements containing tag and publisher, publisher might
        # be empty
        tag_publisher = chart_song.find("td", class_="c3").find_all("div")
        # finds the div element contaning the song title
        song_title = chart_song.find("div",
                                     class_="chart-section-element-title") \
            .get_text().strip()
        # finds the div element contaning the artist name
        artist_name = chart_song.find("div",
                                      class_="chart-section-element-author") \
            .get_text().strip()
        # gets the tag from tag_publisher
        tag = tag_publisher[0].get_text().strip()
        # gets the publisher from tag_publisher
        publisher = tag_publisher[1].get_text().strip()
        # finds the td element contaning the current rank of the song
        curr_rank = chart_song.find("td", class_="c4").get_text().strip()
        # finds the td element contaning the previous rank of the song
        prev_rank = chart_song.find("td", class_="c5").get_text().strip()
        # finds the td element containing how low the song has been on the chart
        n_weeks = chart_song.find("td", class_="c6").get_text().strip()

        out.append([
            unidecode(curr_rank),
            unidecode(song_title.lower()),
            unidecode(artist_name.lower()),
            unidecode(tag.lower()),
            unidecode(publisher.lower()),
            unidecode(prev_rank),
            unidecode(n_weeks),
            date_match
        ])
    return out


if __name__ == "__main__":
    # Create download folder if not present
    try:
        download_path = os.path.join(DOWNLOAD_DIR, CHART_NAME)
        os.makedirs(download_path)
    except FileExistsError:
        pass

    unique_songs = []

    year = START_DATE

    while year <= END_DATE:
        week = 1
        while week <= 52:
            current_date = f"/{year}/{week}"
            chart_url = FIMI_URL + current_date
            csv_filename = DOWNLOAD_DIR + "/" + CHART_NAME + "/" + f"{year}-{week}" \
                           + "_" + CHART_NAME + ".csv"
            soup = get_html(chart_url)
            songs_data = get_songs(soup)
            if not songs_data:
                logging.warning(f"week {week} missing")
                week += 1
                continue
            if VERBOSE:
                print(current_date)

            with open(csv_filename, "w", newline='',
                      encoding='utf-8') as file_handler:
                # use tab as delimiter since different artist of the same
                # song are separated by commas
                writer = csv.writer(file_handler, delimiter='\t',
                                    quotechar='"', quoting=csv.QUOTE_ALL)
                writer.writerow(FIELD_NAMES)
                for curr_rank, song_title, artist_name, tag, publisher, \
                         prev_rank, n_weeks, date in songs_data:

                    writer.writerow(
                        [curr_rank, song_title, artist_name, tag, publisher,
                         prev_rank, n_weeks, date])

                    # Create of all the unique songs in all the charts
                    entry = f'"{artist_name}";"{song_title}"'
                    if entry not in unique_songs:
                        unique_songs.append(entry)

                    if VERBOSE:
                        print(f"\t{song_title}\t{artist_name}")
            logging.info(f"Parsing {current_date}")

            week += 1
        logging.info(f"end of year {year}")
        year += 1

    driver.quit()
    # ==========================================================================

    if VERBOSE:
        print("Now I'm saving all distinct songs")
    # Save unique songs in a file
    with open("unique_songs.csv", "w") as unique_file:
        unique_file.write("artists;song")
        for song in tqdm(unique_songs):
            unique_file.write("\n" + song)
