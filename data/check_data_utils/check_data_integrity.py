"""
This simple script is a utility to make data cleaning easier.
Write into CSV_PATH the location of the csv you want to clean, then start the script.
The file to clean must be grouped by the unique spotify song.
For every song recorder you will see a grid like so:

original_name       found_name      spotify_id
original_artist     found_artist    similarity

if the original name and the original artist matches the found name and the found
artist just press ENTER. Otherwise search for the spotify id, paste it and press
ENTER. If you can't find the spotify id write "???" and press ENTER.

If you want to stop the process, just write "quit!". BEWARE!!!!!!!!
Doinso you will delete everything and you will need to do everything again.

At the end this script will write tuples of (old_id, new_id) in a file that will be
further processed
"""
from difflib import SequenceMatcher
import re

import pandas as pd
import matplotlib.pyplot as plt

CSV_PATH = "/home/giuseppe/Documents/Master/progetto/data/cleaned_df_FINALISSIMISSIMO_2006_2021.csv"
ONLY_GRAPH = False


def group_by_names(ungrouped_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a dataframe grouped by artist and song names
    Parameters
    ----------
    ungrouped_df :  pd.DataFrame

    Returns
    -------
    pd.DataFrame

    """
    return ungrouped_df.groupby("artist_and_name").first().reset_index()


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


df = pd.read_csv(CSV_PATH, sep=";")
df["artist_and_name"] = df["original_song_name"] + " " + df["original_artists_name"]
df = group_by_names(df)
unique_names_df = df[["original_song_name", "song_name",
                      "song_id", "artist_and_name",
                      "original_artists_name", "artists_names"]]

sim_score = []
unique_names_df = unique_names_df.dropna().copy()
for unique_names_id, row_series in unique_names_df.iterrows():
    o_name = re.sub(r"[\W_]+", " ",
                    row_series["original_song_name"]).lower().strip()
    f_name = re.sub(r"[\W_]+", " ",
                    row_series["song_name"]).lower().strip()
    o_artist = re.sub(r"[\W_]+", " ",
                      row_series["original_artists_name"]).lower().strip()
    f_artist = re.sub(r"[\W_]+", " ",
                      row_series["artists_names"]).lower().strip()
    sim_score.append((unique_names_id, apply_sm(o_name + " " + o_artist,
                                                f_name + " " + f_artist)))

scores = pd.DataFrame(sim_score, columns=["id", "score"]).set_index("id")
unique_names_df = unique_names_df.reset_index()
scores_df = unique_names_df.merge(scores,
                                  left_on="index",
                                  right_on='id')
scores_df.sort_values(by="score", inplace=True)
scores_df = scores_df.set_index("index")

fig, ax = plt.subplots(figsize=plt.figaspect(1))
ax.hist(scores_df["score"], bins=5)
ax.set(xlabel="similarity", ylabel="count")
plt.savefig("similarity_score_QC.png", dpi=300, transparent=True)
