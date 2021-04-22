import logging
import csv
import json
from pprint import pprint
from string import punctuation

from tqdm import tqdm
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def search_song(query):
    return sp.search(q=query, type='track', market="IT", limit=1)


logging.basicConfig(format='%(levelname)s\t%(message)s',
                    filename="spotify_parsing.log",
                    filemode="w",
                    level=logging.INFO)

with open("./spotify_keys.txt", "r") as spotify_keys:
    keys = dict()
    for key_string in spotify_keys.readlines():
        key, value = key_string.strip().split(": ")
        keys[key] = value

credentials = SpotifyClientCredentials(client_id=keys["clientID"],
                                       client_secret=keys["client_secret"])
sp = spotipy.Spotify(client_credentials_manager=credentials)
