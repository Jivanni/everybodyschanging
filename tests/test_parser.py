import csv
import logging
import mmap
from string import punctuation
from typing import Optional, Dict

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm

SONGS_PATH = "../scraper/top40_scraper/unique_songs.csv"


def get_num_lines(file_path: str) -> int:
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines - 1



def get_spotify_keys():
    with open("../spotify_info/spotify_keys.txt", "r") as spotify_keys:
        client_keys = dict()
        for key_string in spotify_keys.readlines():
            key, value = key_string.strip().split(": ")
            client_keys[key] = value
    return client_keys

def get_song(query):
    return sp.search(q=query, type='track', market="IT", limit=1)


logging.basicConfig(format='%(levelname)s\t%(message)s',
                    filename="spotify_parsing.log",
                    filemode="w",
                    level=logging.INFO)

spotify_features_head = ['artist_name', 'song_name', 'danceability',
                         'energy', 'key', 'loudness',
                         'mode', 'speechiness', 'acousticness',
                         'instrumentalness', 'liveness', 'valence',
                         'tempo', 'type', 'id', 'uri', 'track_href',
                         'analysis_url', 'duration_ms',
                         'time_signature']

if __name__ == "__main__":
    keys = get_spotify_keys()

    credentials = SpotifyClientCredentials(client_id=keys["clientID"],
                                           client_secret=keys["client_secret"])
    sp = spotipy.Spotify(client_credentials_manager=credentials)


    print(get_song("3kFQ2djY3O2uH8o0WsqdhO"))
