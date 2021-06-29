import os
import json
import csv
from difflib import SequenceMatcher
from string import punctuation
from typing import Tuple, Optional, List, Dict, Any

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

DIRTY_CSV_DIR = "/home/giuseppe/Documents/Master/progetto/data/splitaa"
CLEAN_CSV_DIR = "/home/giuseppe/Documents/Master/progetto/data" \
                "cleaned_aa.csv"
KEYS_PATH = "/home/giuseppe/Documents/Master/progetto/initial_data_gathering" \
            "/spotify_info/spotify_keys_2.txt"
JSON_PATH = "/home/giuseppe/Documents/Master/progetto/conv_dict.json"

ORIGINAL_FEATURES = ['original_song_name', 'original_artists_name',
                     'curr_rank', 'tag_fimi', 'publisher', 'date_chart']


# ['original_song_name', 'original_artists_name', 'curr_rank',
# 'tag_fimi', 'publisher', 'date_chart', 'album_release_date',
# 'album_type', 'song_name', 'album_id', 'artists_names', 'artists_id',
# 'explicit', 'duration', 'song_id', 'popularity', 'danceability', 'energy',
# 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness',
# 'liveness', 'valence', 'tempo', 'type', 'id', 'uri', 'track_href',
# 'analysis_url', 'duration_ms', 'time_signature']


def update_dict(toupdaterow: Dict, sp_features: Dict, af: Dict):
    af.update(sp_features)
    toupdaterow.update(af)
    print(af)
    return toupdaterow, af


def clean_string(dirty_string: str) -> str:
    cleaned_string = dirty_string.lower()
    cleaned_string = cleaned_string.translate(str.maketrans('',
                                                            '',
                                                            punctuation))
    return cleaned_string


def apply_sm(str_1: str, str_2: str) -> float:
    """
    Returns the "similarity" between two strings.
    Parameters
    ----------
    str_1 : str
    str_2 :  str

    Returns
    -------
    float
    """
    return SequenceMatcher(None, str_1, str_2).ratio()


def check_similarity(names: Tuple[str, str],
                     artists: Tuple[str, str],
                     threshold: float = 0.9) -> bool:
    """
    This function checks if the original name or the artists names are similar.
    Parameters
    ----------
    threshold : float
    names : Tuple[str, str]
    artists : Tuple[str, str]

    Returns
    -------
    bool
        true if name or artists are different, false otherwise
    """
    sm_names = apply_sm(*names)
    sm_artists = apply_sm(*artists)
    return True if sm_names < threshold or sm_artists < threshold else False


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


def get_features_from_id(query: str,
                         sp_obj: spotipy.client.Spotify) -> Optional[Dict[str,
                                                                          str]]:
    """
    Utility function that return the track features given a query and a spotipy
    search object
    Parameters
    ----------
    query : str
    sp_obj : spotipy.client.Spotify

    Returns
    -------
    Optional[Dict[str, str]]
    """
    track_id = sp_obj.search(q=query, type='track', market="IT", limit=20)
    try:
        first_track = track_id["tracks"]["items"][0]
        track_feat = get_song_features(first_track)
    except IndexError:
        return None
    return track_feat


def get_feature_and_check(singer: str,
                          track: str,
                          sp_obj: spotipy.client.Spotify) -> Optional[Dict[str,
                                                                           str]]:
    """
    This function takes a singer and the name of a track and returns
    the spotify features for that particular track if he can find the track
    otherwise it will return None
    Parameters
    ----------
    sp_obj : spotipy.client.Spotify
    singer : str
    track : str

    Returns
    -------
    Optional[Dict[str, str]
        an id if it found the song, None otherwise
    """
    possible_queries = [
        f'artist:{singer} track:{track}',
        f'track:{track}',
        f'artist: {singer} {track}',
    ]
    # try all possible queries. There are bugs in the api that makes harder
    # to handle certain types of track names. Therefore I created some options to
    # avoid those bugs. Some are riskier than others
    for query in possible_queries:
        track_feat = get_features_from_id(query, sp_obj)
        if track_feat is not None:
            return track_feat
    return None


# cache dictionary
if os.path.exists(JSON_PATH):
    with open(JSON_PATH) as json_conv:
        conversion_dict = json.load(json_conv)
else:
    conversion_dict = {}
if __name__ == '__main__':

    keys = get_spotify_keys(KEYS_PATH)

    # Create credential for the api
    credentials = SpotifyClientCredentials(client_id=keys["clientID"],
                                           client_secret=keys["client_secret"])
    # Instantiate the API
    sp = spotipy.Spotify(client_credentials_manager=credentials)

    nrows = 0
    with open(DIRTY_CSV_DIR, "r", encoding="utf8") as temp:
        for line in temp:
            nrows += 1

    line_count = 0
    with open(DIRTY_CSV_DIR, "r",
              encoding="utf8") as dirty_csv, open(CLEAN_CSV_DIR, "w+",
                                                  encoding="utf8") as clean_csv:
        reader = csv.DictReader(dirty_csv, delimiter=";")
        writer = csv.DictWriter(clean_csv, delimiter=";",
                                fieldnames=reader.fieldnames)
        print(reader.fieldnames)
        #quit()
        writer.writeheader()
        for row in reader:
            print(line_count)
            line_count += 1
            o_name = clean_string(row["original_song_name"])
            o_artists = clean_string(row["original_artists_name"])

            f_name = clean_string(row["song_name"])
            f_artists = clean_string(row["artists_names"])

            combined_originals = o_name[:20] + o_artists[:20]
            features = conversion_dict.get(combined_originals)

            if features is None:
                # if names or songs are not similar
                if check_similarity((o_name, f_name),
                                    (o_artists, f_artists)):
                    song_features = get_feature_and_check(singer=o_artists,
                                                          track=o_name,
                                                          sp_obj=sp)
                    # if the automatic search couldn't find a song
                    if song_features is None:
                        # ask to find the id
                        print(line_count / nrows)
                        print(f"{o_name}\t{o_artists}\nNot found")
                        new_id = input("Can you find it? ")
                        if new_id == "quit!":
                            break
                        elif len(new_id) > 3:
                            song_feature = get_song_features(sp.track(new_id))
                            features_dict = sp.audio_features(new_id)[0]
                            row, fts = update_dict(row, sp_features=song_feature,
                                                   af=features_dict)
                            conversion_dict[combined_originals] = fts
                            writer.writerow(row)
                        else:
                            conversion_dict[combined_originals] = "???"
                            continue
                    # if i found a song then ask if it is the right song
                    else:
                        f_name = song_features["song_name"]
                        f_artists = song_features["artists_names"]
                        print(line_count / nrows)
                        print(f"Originals:\t{o_name[:30]}\t{o_artists[:30]}\n"
                                f"I found:\t{f_name[:30]}\t{f_artists[:30]}")
                        new_id = input("is it right? ")
                        # if = 3 then i can't find a right id
                        if len(new_id) == 3:
                            conversion_dict[combined_originals] = "???"
                            continue
                        elif new_id == "quit!":
                            break
                        # if > 3 i found an id
                        elif len(new_id) > 3:
                            song_feature = get_song_features(sp.track(new_id))
                            features_dict = sp.audio_features(new_id)[0]
                            row, feats = update_dict(row, sp_features=song_feature,
                                                     af=features_dict)
                            conversion_dict[combined_originals] = feats
                            writer.writerow(row)
                        # otherwise the song found is right
                        else:
                            audio_features = \
                                sp.audio_features(song_features["song_id"])[0]
                            row, feats = update_dict(row, sp_features=song_features,
                                                     af=audio_features)
                            conversion_dict[combined_originals] = feats
                            writer.writerow(row)
                # if names are similar
                else:
                    row_copy = row.copy()
                    for original_feature in ORIGINAL_FEATURES:
                        row_copy.pop(original_feature)
                    conversion_dict[combined_originals] = row_copy
                    row.update(row_copy)
                    writer.writerow(row)
            # if features are in the dictionary
            else:
                if conversion_dict[combined_originals] != "???":
                    row.update(conversion_dict[combined_originals])
                    writer.writerow(row)

            with open(JSON_PATH, "w") as json_conv:
                json.dump(conversion_dict, json_conv)
