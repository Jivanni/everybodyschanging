"""
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
"""
import time
import json
import csv

import pandas as pd

from tqdm import tqdm

import spotipy
from spotify_info.spotify_parser import get_song_features, get_spotify_keys
from spotify_info.spotify_parser import get_num_lines
from spotipy.oauth2 import SpotifyClientCredentials

sp_keys = get_spotify_keys("./spotify_info/spotify_keys.txt")
keys = get_spotify_keys("spotify_info/spotify_keys.txt")
# Create credential for the api
credentials = SpotifyClientCredentials(client_id=keys["clientID"],
                                       client_secret=keys["client_secret"])
# Instantiate the API
sp = spotipy.Spotify(client_credentials_manager=credentials, retries=10)
DATA_PATH = "../data/cleaned_df_FINALISSIMISSIMO_2006_2021.csv"

scraper_df = pd.read_csv("../data/check_data_utils/scraper_df.csv", sep=";")
spotify_df = pd.read_csv("../data/check_data_utils/spotify_df.csv", sep=";")

spotify_df["song_id"] = spotify_df["song_id"].astype(str)

with open("../ultimate_conversion_dict.json",
          "r") as u_json:
    c_json = json.load(u_json)


TOTAL_LINES = get_num_lines("../data/check_data_utils/spotify_df.csv")

with open("../data/check_data_utils/spotify_df.csv", "r",
        encoding="utf8") as sp_csv, open("../data/check_data_utils/spotify_df_cl.csv",
                  "w", encoding="utf8") as sp_writer:

    sp_reader = csv.reader(sp_csv, delimiter=";")
    sp_writer = csv.writer(sp_writer, delimiter=";")
    for line in sp_reader:
        internal_id = line[0]
        spotify_id = line[22]

        if internal_id in c_json:
            right_id = c_json[internal_id]
            song_feature = get_song_features(sp.track(spotify_id))
            for feat in sp.audio_features(spotify_id):
                if feat is not None:
                    song_audio_feats = feat
                    break
            sp_writer.writerow([
                internal_id,
                song_feature['album_release_date'],
                song_feature['album_type'],
                song_feature['song_name'],
                song_feature['album_id'],
                song_feature['artists_names'],
                song_feature['artists_id'],
                song_feature['explicit'],
                song_feature['duration'],
                song_feature['popularity'],
                song_audio_feats['danceability'],
                song_audio_feats['energy'],
                song_audio_feats['key'],
                song_audio_feats['loudness'],
                song_audio_feats['mode'],
                song_audio_feats['speechiness'],
                song_audio_feats['acousticness'],
                song_audio_feats['instrumentalness'],
                song_audio_feats['liveness'],
                song_audio_feats['valence'],
                song_audio_feats['tempo'],
                song_audio_feats['type'],
                song_audio_feats['id'],
                song_audio_feats['uri'],
                song_audio_feats['track_href'],
                song_audio_feats['analysis_url'],
                song_audio_feats['duration_ms'],
                song_audio_feats['time_signature']
            ])

        else:
            sp_writer.writerow(line)

