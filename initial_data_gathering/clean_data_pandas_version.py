"""
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
"""
import json

import pandas as pd

from tqdm import tqdm

import spotipy
from spotify_info.spotify_parser import get_song_features, get_spotify_keys
from spotipy.oauth2 import SpotifyClientCredentials

sp_keys = get_spotify_keys("./spotify_info/spotify_keys.txt")
keys = get_spotify_keys("spotify_info/spotify_keys.txt")
# Create credential for the api
credentials = SpotifyClientCredentials(client_id=keys["clientID"],
                                       client_secret=keys["client_secret"])
# Instantiate the API
sp = spotipy.Spotify(client_credentials_manager=credentials, retries=10)
DATA_PATH = "../data/cleaned_df_FINALISSIMISSIMO_2006_2021.csv"

scraper_df = pd.read_csv("../data/check_data_utils/scraper_df.csv")
spotify_df = pd.read_csv("../data/check_data_utils/spotify_df.csv")

spotify_df["song_id"] = spotify_df["song_id"].astype(str)

with open("../data/check_data_utils/ultimate_conversion_dict.json",
          "r") as u_json:
    c_json = json.load(u_json)

none_rows = list(c_json.keys())
clean_spotify_df = spotify_df.set_index("song_id").drop(none_rows)

features_conversion_dict = {'song_id': [],
                            'album_release_date': [],
                            'album_type': [],
                            'song_name': [], 'album_id': [],
                            'artists_names': [], 'artists_id': [],
                            'explicit': [], 'duration': [],
                            'popularity': [], 'danceability': [],
                            'energy': [], 'key': [],
                            'loudness': [],
                            'mode': [], 'speechiness': [],
                            'acousticness': [],
                            'instrumentalness': [],
                            'liveness': [], 'valence': [],
                            'tempo': [],
                            'type': [], 'id': [], 'uri': [],
                            'track_href': [],
                            'analysis_url': [], 'duration_ms': [],
                            'time_signature': []}

for s_id, right_id in tqdm(c_json.items()):
    if len(right_id) == 0:
        continue
    song_feature = get_song_features(sp.track(right_id))
    for feat in sp.audio_features(right_id):
        if feat is not None:
            song_audio_feats = feat
            break
    features_conversion_dict['song_id'].append(s_id)
    features_conversion_dict['album_release_date'].append(
        song_feature['album_release_date']
    )
    features_conversion_dict['album_type'].append(song_feature['album_type'])
    features_conversion_dict['song_name'].append(song_feature['song_name'])
    features_conversion_dict['album_id'].append(song_feature['album_id'])
    features_conversion_dict['artists_names'].append(song_feature['artists_names'])
    features_conversion_dict['artists_id'].append(song_feature['artists_id'])
    features_conversion_dict['explicit'].append(song_feature['explicit'])
    features_conversion_dict['duration'].append(song_feature['duration'])
    features_conversion_dict['popularity'].append(song_feature['popularity'])
    features_conversion_dict['danceability'].append(song_audio_feats['danceability'])
    features_conversion_dict['energy'].append(song_audio_feats['energy'])
    features_conversion_dict['key'].append(song_audio_feats['key'])
    features_conversion_dict['loudness'].append(song_audio_feats['loudness'])
    features_conversion_dict['mode'].append(song_audio_feats['mode'])
    features_conversion_dict['speechiness'].append(song_audio_feats['speechiness'])
    features_conversion_dict['acousticness'].append(song_audio_feats['acousticness'])
    features_conversion_dict['instrumentalness'].append(
        song_audio_feats['instrumentalness']
    )
    features_conversion_dict['liveness'].append(song_audio_feats['liveness'])
    features_conversion_dict['valence'].append(song_audio_feats['valence'])
    features_conversion_dict['tempo'].append(song_audio_feats['tempo'])
    features_conversion_dict['type'].append(song_audio_feats['type'])
    features_conversion_dict['id'].append(song_audio_feats['id'])
    features_conversion_dict['uri'].append(song_audio_feats['uri'])
    features_conversion_dict['track_href'].append(song_audio_feats['track_href'])
    features_conversion_dict['analysis_url'].append(song_audio_feats['analysis_url'])
    features_conversion_dict['duration_ms'].append(song_audio_feats['duration_ms'])
    features_conversion_dict['time_signature'].append(
        song_audio_feats['time_signature']
    )

cleaned_df_part = pd.DataFrame.from_dict(features_conversion_dict)
whole_spotify_df = pd.concat([clean_spotify_df, cleaned_df_part])

whole_spotify_df.to_csv("../only_songs.csv", index=False)
scraper_df.to_csv("../only_chart.csv", index=False)
