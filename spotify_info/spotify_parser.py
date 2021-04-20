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


def get_id(singer: str, track: str) -> Optional[str]:
    query = f'artist:{singer} track:{track}'
    track_id = sp.search(q=query, type='track',
                         market="IT", limit=1)
    if len(track_id["tracks"]["items"]) != 0:
        track_id = track_id["tracks"]["items"][0]["id"]
    else:
        query = f'track:{track}'
        track_id = sp.search(q=query, type='track',
                             market="IT", limit=1)
        if len(track_id["tracks"]["items"]) != 0:
            track_id = track_id["tracks"]["items"][0]["id"]
        else:
            logging.warning(f"{query} not found")

            return None

    return track_id


def get_spotify_keys() -> Dict[str: str]:
    with open("./spotify_keys.txt", "r") as spotify_keys:
        client_keys = dict()
        for key_string in spotify_keys.readlines():
            key, value = key_string.strip().split(": ")
            client_keys[key] = value
    return client_keys


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

    with open(SONGS_PATH, "r") as songs_file, open("./spotify_features.csv", "w") as features_file:
        next(songs_file)  # skip header
        songs_reader = csv.reader(songs_file, delimiter=";")
        spotify_features_writer = csv.writer(features_file, delimiter=";")
        spotify_features_writer.writerow(spotify_features_head)

        for artist, song in tqdm(songs_reader, total=get_num_lines(SONGS_PATH), desc="Parsing the songs"):
            cleaned_artist = artist.translate(str.maketrans(punctuation, ' ' * len(punctuation)))
            cleaned_song = song.translate(str.maketrans(punctuation, ' ' * len(punctuation)))

            song_id = get_id(cleaned_artist, cleaned_song)

            # if I cannot find the song skip the loop
            if song_id is None:
                continue

            features_dict = sp.audio_features(song_id)[0]

            spotify_features_writer.writerow([
                artist, song,
                features_dict['danceability'], features_dict['energy'],
                features_dict['key'], features_dict['loudness'],
                features_dict['mode'], features_dict['speechiness'],
                features_dict['acousticness'],
                features_dict['instrumentalness'], features_dict['liveness'],
                features_dict['valence'], features_dict['tempo'],
                features_dict['type'], features_dict['id'],
                features_dict['track_href'], features_dict['analysis_url'],
                features_dict['duration_ms'], features_dict['time_signature']
            ])
