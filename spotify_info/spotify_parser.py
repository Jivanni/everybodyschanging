"""Spotify parser

This script takes a csv file with ; as separator of a song and an artist
and searches on spotify the song creating a csv with the features taken
from spotify

A file called spotify_keys.txt where both spotify keys must be stored.

This script requires spotipy and tqdm to be installed

This file is designed to run stand alone.
"""
import csv
import logging
import mmap
from string import punctuation
from typing import Any, Dict, Optional

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm

SONGS_PATH = "../scraper/top40_scraper/unique_songs.csv"

logging.basicConfig(format='%(levelname)s\t%(message)s',
                    filename="spotify_parsing.log",
                    filemode="w",
                    level=logging.INFO)

spotify_features_head = [
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


def get_spotify_keys(path: str = "./spotify_keys.txt") -> Dict[str, str]:
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
    except FileNotFoundError:
        raise FileNotFoundError("You don't have a file named 'spotify_keys.txt'"
                                " that should contain both API keys!")


def get_num_lines(file_path: str) -> int:
    """
    Utility function used to calculate the length of a file
    Parameters
    ----------
    file_path : str
        location of the file
    Returns
    -------
    int
        number of line in the file
    """
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines - 1


def get_song_features(track_features: Dict[str, Any]) -> Dict[str, str]:
    """
    This function takes part of the output of a track searched with spotify
    and return a dictionary with some features extracted from the api
    Parameters
    ----------
    track_features : Dict[str, Any]

    Returns
    -------
    Dict[str, str]
    """
    # Get the first track that match the query
    album_id = track_features["album"]["id"]
    album_release_date = track_features["album"]["release_date"]
    album_type = track_features["album"]["album_type"]
    artists_names = [
        artst["name"]
        for artst in track_features["artists"]
    ]
    artists_id = [
        artst["id"]
        for artst in track_features["artists"]
    ]
    explicit: bool = track_features["explicit"]
    song_name: bool = track_features["name"]
    duration: int = track_features["duration_ms"]
    s_id: str = track_features["id"]
    popularity: int = track_features["popularity"]

    out_dict = {
        "album_release_date": album_release_date,
        "album_type": album_type,
        "song_name": song_name,
        "album_id": album_id,
        "artists_names": artists_names,
        "artists_id": artists_id,
        "explicit": explicit,
        "duration": duration,
        "song_id": s_id,
        "popularity": popularity,
    }
    return out_dict


def get_feature_and_check(singer: str, track: str) -> Optional[Dict[str, str]]:
    """
    This function takes a singer and the name of a track and returns
    the spotify features for that particular track if he can find the track
    otherwise it will return None
    Parameters
    ----------
    singer : str
    track : str

    Returns
    -------
    Optional[Dict[str, str]
        an id if it found the song, None otherwise
    """
    query = f'artist:{singer} track:{track}'
    track_id = sp.search(q=query, type='track',
                         market="IT", limit=1)
    try:
        track_feat = get_song_features(track_id['tracks']['items'][0])
    except IndexError:
        # if it can't find the track maybe it's because the artist is misspelled
        query = f'track:{track}'
        track_id = sp.search(q=query, type='track',
                             market="IT", limit=1)
        try:
            track_feat = get_song_features(track_id["tracks"]["items"][0])
        except IndexError:
            # if it can't find the track return None
            logging.warning(f"{query} not found")

            return None

    return track_feat


if __name__ == "__main__":
    keys = get_spotify_keys()

    # Create credential for the api
    credentials = SpotifyClientCredentials(client_id=keys["clientID"],
                                           client_secret=keys["client_secret"])
    # Instanciate the API
    sp = spotipy.Spotify(client_credentials_manager=credentials)

    with open(SONGS_PATH, "r",
              encoding="utf8") as songs_file, open("./spotify_features.csv", "w",
                                                   encoding="utf8") as features_file:
        next(songs_file)  # skip header
        songs_reader = csv.reader(songs_file, delimiter=";")
        spotify_features_writer = csv.writer(features_file, delimiter=";")
        spotify_features_writer.writerow(spotify_features_head)

        for artist, song in tqdm(songs_reader,
                                 total=get_num_lines(SONGS_PATH),
                                 desc="Parsing the songs"):
            # remove strange char that can mislead the searcher
            cleaned_artist = artist.translate(str.maketrans(punctuation,
                                                            ' ' * len(punctuation)))
            cleaned_song = song.translate(str.maketrans(punctuation,
                                                        ' ' * len(punctuation)))
            # return the features of a song
            song_feat = get_feature_and_check(cleaned_artist, cleaned_song)
            # if I cannot find the song skip the loop
            if song_feat is None:
                continue

            song_id = song_feat["song_id"]
            # return the audio features by Spotify
            features_dict = sp.audio_features(song_id)[0]
            spotify_features_writer.writerow([
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

            if isinstance(song_feat["song_name"], list):
                s_name = ", ".join(song_feat["song_name"])
            else:
                s_name = song_feat["song_name"]
            a_name = song_feat["artists_names"]
            logging.info(f"{s_name} by {s_name}"
                         f", id:{song_id} written to file")
