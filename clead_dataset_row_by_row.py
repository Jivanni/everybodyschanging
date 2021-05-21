"""
This script takes a dirty csv and using a json file converts it into a clean csv file
"""
import csv
import json
import logging

from tqdm import tqdm

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

from spotify_info.spotify_parser import get_spotify_keys, get_song_features
from spotify_info.spotify_parser import get_num_lines


logging.basicConfig(format='%(levelname)s\t%(message)s',
                    filename="rbr_cleaning.log",
                    filemode="w",
                    level=logging.INFO)

DIRTY_CSV = "data/cleaned_df_v8.csv"
CLEAN_CSV = "data/cleaned_df_v9.csv"
CONVERSION_JSON = "data/check_data_utils/redundant_conversion.json"
TOTAL_LINES = get_num_lines(DIRTY_CSV)

sp_keys = get_spotify_keys("./spotify_info/spotify_keys.txt")

keys = get_spotify_keys("spotify_info/spotify_keys.txt")

# Create credential for the api
credentials = SpotifyClientCredentials(client_id=keys["clientID"],
                                       client_secret=keys["client_secret"])
# Instantiate the API
sp = spotipy.Spotify(client_credentials_manager=credentials, retries=10)

with open(CONVERSION_JSON, "r", encoding="utf8") as json_f:
    conversion_dict = json.load(json_f)

with open(DIRTY_CSV, "r",
          encoding="utf8") as dirty_file, open(CLEAN_CSV, "w",
                                               encoding="utf8") as clean_file:
    dirty_reader = csv.reader(dirty_file, delimiter=";")
    clean_writer = csv.writer(clean_file, delimiter=";")

    for row in tqdm(dirty_reader, total=TOTAL_LINES):
        o_track_name = row[0][:40]
        o_artist_name = row[1][:40]
        combined_originals = f"{o_track_name} {o_artist_name}"
        # if the combined keys are in the conversion dict modify the row
        if combined_originals in conversion_dict:

            right_id = conversion_dict[combined_originals]
            # if the id is None than write the row as it is and skip this iteration
            if right_id == "None":
                clean_writer.writerow(row)
                continue
            # empty id means that the original id was right
            if right_id == "":
                clean_writer.writerow(row)
                continue

            # if it can't find the id then skip this row
            try:
                song_feature = get_song_features(sp.track(right_id))
            except SpotifyException as exception:
                logging.warning("%s not found. id:\t%s",
                                combined_originals, right_id)
                clean_writer.writerow(row)
                continue

            song_audio_feats = sp.audio_features(right_id)

            # take the first non non auto feature
            for feat in song_audio_feats:
                if feat is not None:
                    song_audio_feats = feat
                    break

            clean_writer.writerow([
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                song_feature["album_release_date"],
                song_feature["album_type"],
                song_feature["song_name"],
                song_feature["album_id"],
                song_feature["artists_names"],
                song_feature["artists_id"],
                song_feature["explicit"],
                song_feature["duration"],
                row[14],
                song_feature["popularity"],
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
                song_audio_feats['track_href'],
                song_audio_feats['analysis_url'],
                song_audio_feats['duration_ms'],
                song_audio_feats['time_signature']
            ])
        else:
            clean_writer.writerow(row)
