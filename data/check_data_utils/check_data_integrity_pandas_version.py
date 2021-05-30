"""
I hope this is the last script used for cleaning the data.
"""
import json
import re
from difflib import SequenceMatcher

import pandas as pd

DATA_PATH = "../cleaned_df_FINALISSIMISSIMO_2006_2021.csv"


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


df = pd.read_csv(DATA_PATH, sep=";", parse_dates=True,
                 keep_default_na=False)
# remove all rows not found
none_rows = [row_id
             for row_id, row in df.iterrows()
             if row["danceability"] == ""
             ]
df = df.drop(none_rows).copy()

df["song_id"] = df["id"]

# the old song_id was rubbish, in this way I give each song a numerical identifier
pclass_dict = {o_id: n_id
               for n_id, o_id in enumerate(df["song_id"].unique())}
df["song_id"] = df["song_id"].map(pclass_dict)

scraper_features = ['original_song_name', 'original_artists_name',
                    'curr_rank', 'tag_fimi',
                    'publisher', 'date_chart', "song_id"]
spotify_features = [
                       column
                       for column in df.columns
                       if column not in scraper_features
                   ] + ["song_id"]
scraper_df = df[scraper_features]
spotify_df = df[spotify_features].groupby("song_id").first()

g_scraper_df = scraper_df.groupby("song_id").first()
conversion_dict = {}
for spotify_id, spotify_row in spotify_df.iterrows():
    scraper_row = g_scraper_df.iloc[spotify_id]

    c_date = scraper_row["date_chart"]

    o_artist_name = scraper_row["original_artists_name"][:40]
    o_track_name = scraper_row["original_song_name"][:40]

    f_artist_name = spotify_row["artists_names"][:40]
    f_artist_name = re.sub(r"[\W_]+", " ",
                           f_artist_name).lower().strip()
    f_track_name = spotify_row["song_name"][:40]
    f_track_name = re.sub(r"[\W_]+", " ",
                          f_track_name).lower().strip()

    sm = apply_sm(o_artist_name, f_artist_name)

    if sm < 0.6:
        print(f"\n{c_date}\n"
              f"found: {f_artist_name:40}\t{f_track_name:40}\n"
              f"orign: {o_artist_name:40}\t{o_track_name:40}")
        new_id = input("Is this fucking valid? ")
        if len(new_id) > 15:
            conversion_dict[spotify_id] = new_id
        elif new_id == "quit!":
            break
        elif len(new_id) == 0:
            pass
        else:
            conversion_dict[spotify_id] = ""

with open("ultimate_conversion_dict.json", "w") as c_json:
    json.dump(conversion_dict, c_json)
