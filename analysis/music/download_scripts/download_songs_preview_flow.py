"""
This script loads a csv containing the charts parsed from spotify, group them
by Spotify ID and then downloads the Spotify preview for the given track.

This script uses the code authorizaton flow API, I found the authentication
code on StackOverflow. I don't know how it works, I don't know why it works
but it works. And that's good enough for me.
"""
import os
import re
import csv
import logging
from string import punctuation
from typing import Optional, Dict

import requests
import pandas as pd
from tqdm import tqdm

import spotipy
from spotipy.oauth2 import SpotifyOAuth

logging.basicConfig(format='%(levelname)s\t%(message)s',
                    filename="dw_songs.log",
                    filemode="w",
                    level=logging.INFO)

DATA_PATH = "../../../data/cleaned_df_v2.csv"
DOWNLOAD_FOLDER = "../preview_download"

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


redirect_URI = "http://localhost:8000"
scope = "user-library-read"
keys = get_spotify_keys("../../../initial_data_gathering/"
                        "spotify_info/spotify_keys_2.txt")

sp_oauth = SpotifyOAuth(client_id=keys["clientID"],
                        client_secret=keys["client_secret"],
                        redirect_uri=redirect_URI,
                        scope=scope)
token_info = sp_oauth.get_cached_token()
if not token_info:
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    response = input('Paste the above link into your browser, '
                     'then paste the redirect url here: ')

    code = sp_oauth.parse_response_code(response)
    token_info = sp_oauth.get_access_token(code)

token = token_info['access_token']

sp = spotipy.Spotify(auth=token)



df = pd.read_csv(DATA_PATH, sep=";",
                 low_memory=False, parse_dates=True)
only_songs = df.groupby("id").first().reset_index()

none_counter = 0
for df_id, df_row in tqdm(only_songs.iterrows(),
                          total=only_songs.shape[0]):
    song_id = df_row["id"]
    name_file = song_id.strip() + ".mp3"
    file_path = os.path.join(DOWNLOAD_FOLDER, name_file)
    if os.path.exists(file_path):
        continue

    sp_api_output = sp.track(song_id)
    preview_url = sp_api_output["preview_url"]
    if preview_url is None:
        none_counter += 1
        logging.warning("%s\t not found", song_id)
        continue
    req = requests.get(preview_url, allow_redirects=True)

    with open(file_path, 'wb') as f:
        f.write(req.content)

print(f"not cannot find {none_counter} songs. Total: {only_songs.shape[0]}")

