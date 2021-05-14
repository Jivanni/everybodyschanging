"""
This script takes the file in output from the scraping and corrects the findings
according to a json file created with ``create_json_converter.py``
"""
import csv
import json

from spotify_info.spotify_parser import get_song_features

DIRTY_FILE = "./data/download_df.csv"
CLEAN_FILE = "./data/cleaned_df.csv"
CONVERSION_JSON = ""


with open(CONVERSION_JSON) as json_f:
    conversion_dict = json.load(json_f)

with open(DIRTY_FILE,
          "r",
          encoding="utf8") as dirty_file, open(CLEAN_FILE,
                                               "r",
                                               encoding="utf8") as clean_file:
    dirty_reader = csv.reader(dirty_file, delimiter=";")
    clean_writer = csv.writer(clean_file, delimiter=";")

    for row in dirty_reader:

        if row[14] in conversion_dict:
            track_to_clean = conversion_dict[row[14]]
            song_feature = get_song_features(track_to_clean["info"])
            song_audio_feats = track_to_clean["feats"]

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
                song_feature["song_id"],
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
