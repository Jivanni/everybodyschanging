"""
this script takes a chart file containing the spotify id of different songs and
returns a file containing just the song id and the path of the file
"""
import os
import re
import csv
import logging
from typing import Optional, Dict

import requests
import pandas as pd
from tqdm import tqdm

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

logging.basicConfig(format='%(levelname)s\t%(message)s',
                    filename="dw_songs.log",
                    filemode="w",
                    level=logging.INFO)

DOWNLOAD_FOLDER = "preview_download"


def get_spotify_keys(path: str = "./spotify_keys.txt") -> Optional[Dict[str,
                                                                        str]]:
    """
    Function that reads a file where are stored a pair of spotify keys
    Parameters
    -------
    path: str
        path to the file containing the credential keys.
    Returns
    -------
    Dict[str: str]
        return a dictionary with keys "clientID" and "client_secret", whose
        values are the effective keys.
    """
    try:
        with open(path, "r") as spotify_keys:
            client_keys = dict()
            for key_string in spotify_keys.readlines():
                key, value = key_string.strip().split(": ")
                client_keys[key] = value
        return client_keys
    except FileNotFoundError as error:
        print(error,
              "You don't have a file named 'spotify_keys.txt'"
              " that should contain both API keys!")
        return None


if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

keys = get_spotify_keys("../../initial_data_gathering/spotify_info/spotify_keys_2.txt")

# Create credential for the api
credentials = SpotifyClientCredentials(client_id=keys["clientID"],
                                       client_secret=keys["client_secret"])
# Instantiate the API
sp = spotipy.Spotify(auth_manager=credentials)

df = pd.read_csv("../../data/final_df.csv", sep=";",
                 low_memory=False, parse_dates=True)
only_songs = df.groupby("id").first().reset_index()

none_counter = 0
regex = re.compile(".*?\((.*?)\)")
with open("corrispondence_songs.csv", "w") as corr:
    corr_writer = csv.writer(corr, delimiter=",")
    corr_writer.writerow(["id", "filename"])
    for df_id, df_row in tqdm(only_songs.iterrows(),
                              total=only_songs.shape[0]):
        name_file = df_row["song_name"].replace("/", "") \
                                       .strip() \
                                       .replace(" ", "_")

        name_file = re.sub(r'\([^)]*\)', '', name_file)
        name_file += ".mp3"
        file_path = os.path.join(DOWNLOAD_FOLDER, name_file)
        if os.path.exists(file_path):
            continue

        song_id = df_row["id"]
        sp_api_output = sp.track(song_id, market="IT")
        preview_url = sp_api_output["preview_url"]
        if preview_url is None:
            none_counter += 1
            logging.warning("%s\t not found", song_id)
            continue
        req = requests.get(preview_url, allow_redirects=True)

        with open(file_path, 'wb') as f:
            f.write(req.content)

        corr_writer.writerow([song_id, name_file])

print(f"not cannot find {none_counter} songs. Total: {only_songs.shape[0]}")
