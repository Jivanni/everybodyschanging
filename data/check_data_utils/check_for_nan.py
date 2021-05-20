"""
This script will check for NA in the dataset
"""

import csv
import pandas as pd

DATA_PATH = "../cleaned_df_v2.csv"

df = pd.read_csv(DATA_PATH, sep=";")
na_df = df[df["song_name"].isna()]

grouped_na_df = na_df.groupby("song_id").first().reset_index()

conversion_list = []
for _, row in grouped_na_df.iterrows():
    s_id = row["song_id"]
    o_song_name = row["original_song_name"]
    o_artist_name = row["original_artists_name"]
    print(f"{s_id}\t{o_song_name[:20]:20}\t{o_artist_name[:20]:20}")
    new_id = input("Can you find it? ")

    if new_id == "quit!":
        break
    if new_id == "???":
        conversion_list.append((s_id, ""))
    elif len(new_id) != 0:
        conversion_list.append((s_id, new_id))

with open("conversion_id.txt", "w", encoding="utf8") as conv_file:
    for conv_tuple in conversion_list:
        conv_file.write(f"{conv_tuple[0]},{conv_tuple[1]}\n")
