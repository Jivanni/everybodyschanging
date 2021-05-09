"""
Main parser
This script scrape the website of the Federazione Industria Musicale Italiana
(FIMI) And search each song on spotify to retrieve various informations.
"""
import os
import csv
import logging

from tqdm import tqdm
from selenium import webdriver

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from scraper.fimi_scraper.fimi_scraper import get_songs, get_html
from scraper.fimi_scraper.fimi_scraper import DOWNLOAD_DIR, CHART_NAME, FIMI_URL

from spotify_info.spotify_parser import get_spotify_keys, get_feature_and_check

logging.basicConfig(format='%(levelname)s\t%(message)s',
                    filename="main.log",
                    filemode="w",
                    level=logging.INFO)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('window-size=1920x1080')

START_DATE: int = 2013
END_DATE: int = 2015
VERBOSE: bool = True
MAX_WEEKS: int = 60

not_found_songs: int = 0
unique_ids: list = []
spotify_audio_features_dict: dict = {}

spotify_features_head = [
    "original_song_name",
    "original_artists_name",
    "curr_rank",
    "tag_fimi",
    "publisher",
    "date_chart",
    "album_release_date",
    "album_type",
    "song_name",
    "album_id",
    "artists_names",
    "artists_id",
    "explicit",
    "duration",
    "song_id",
    "popularity",
    'danceability',
    'energy',
    'key',
    'loudness',
    'mode',
    'speechiness',
    'acousticness',
    'instrumentalness',
    'liveness',
    'valence',
    'tempo',
    'type',
    'id',
    'uri',
    'track_href',
    'analysis_url',
    'duration_ms',
    'time_signature'
]

if __name__ == "__main__":

    keys = get_spotify_keys("spotify_info/spotify_keys.txt")

    # Create credential for the api
    credentials = SpotifyClientCredentials(client_id=keys["clientID"],
                                           client_secret=keys["client_secret"])
    # Instantiate the API
    sp = spotipy.Spotify(client_credentials_manager=credentials)

    # Create download folder if not present
    try:
        download_path = os.path.join(DOWNLOAD_DIR, CHART_NAME)
        os.makedirs(download_path)
    except FileExistsError:
        pass

    YEAR = START_DATE
    with open("./data/final_df.csv", "w",
              encoding="utf8") as final_csv, webdriver.Chrome(
                                                               options=chrome_options
                                                            ) as webdriver:

        spotify_features_writer = csv.writer(final_csv, delimiter=";")
        spotify_features_writer.writerow(spotify_features_head)

        TOTAL_N_WEEKS = (END_DATE - START_DATE + 1) * MAX_WEEKS

        pbar = tqdm(total=TOTAL_N_WEEKS)
        while YEAR <= END_DATE:
            WEEK = 1
            while WEEK <= MAX_WEEKS:
                current_date = f"/{YEAR}/{WEEK}"
                chart_url = FIMI_URL + current_date
                soup = get_html(chart_url)
                songs_data = get_songs(soup)
                # if no more weeks, skip
                if not songs_data:
                    logging.warning(f"week {WEEK} missing")
                    WEEK += 1
                    not_found_songs += 1
                    pbar.update(1)
                    continue

                for curr_rank, song_title, artist_name, tag, publisher, prev_rank, \
                        n_weeks, date in songs_data:
                    song_feat = get_feature_and_check(artist_name, song_title, sp)
                    # if spotipy can't find the song, move on
                    if song_feat is None:
                        logging.warning(f"track: {song_title} by {artist_name}"
                                        " not found")
                        spotify_features_writer.writerow([
                            song_title,
                            artist_name,
                            curr_rank,
                            tag,
                            publisher,
                            date,
                            "",
                            "",
                            song_title,
                            "",
                            artist_name,
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            ""
                        ])
                        continue

                    song_id = song_feat["song_id"]
                    if song_id not in unique_ids:
                        unique_ids.append(song_id)

                    # return the audio features by Spotify
                    # trying to memoize this step in order to avoid useless
                    # calls to the api
                    if song_id in spotify_audio_features_dict:
                        features_dict = spotify_audio_features_dict[song_id]
                    else:
                        spotify_audio_features_dict[song_id] = sp.audio_features(
                            song_id
                        )[0]
                        features_dict = spotify_audio_features_dict[song_id]

                    spotify_features_writer.writerow([
                        song_title,
                        artist_name,
                        curr_rank,
                        tag,
                        publisher,
                        date,
                        song_feat["album_release_date"],
                        song_feat["album_type"],
                        song_feat["song_name"],
                        song_feat["album_id"],
                        song_feat["artists_names"],
                        song_feat["artists_id"],
                        song_feat["explicit"],
                        song_feat["duration"],
                        song_feat["song_id"],
                        song_feat["popularity"],
                        features_dict['danceability'],
                        features_dict['energy'],
                        features_dict['key'],
                        features_dict['loudness'],
                        features_dict['mode'],
                        features_dict['speechiness'],
                        features_dict['acousticness'],
                        features_dict['instrumentalness'],
                        features_dict['liveness'],
                        features_dict['valence'],
                        features_dict['tempo'],
                        features_dict['type'],
                        features_dict['id'],
                        features_dict['track_href'],
                        features_dict['analysis_url'],
                        features_dict['duration_ms'],
                        features_dict['time_signature']
                    ])
                logging.info(f"Parsing {current_date}")
                WEEK += 1
                pbar.update(1)
            logging.info(f"end of year {YEAR}")
            YEAR += 1

        pbar.close()
    print(f"Parsed from {START_DATE} to {END_DATE}")
    print(f"Found {len(unique_ids)} songs")
    print(f"I couldn't find {not_found_songs} songs on Spotify."
          " Check logs for more information.")
