import csv
from pprint import pprint
from difflib import SequenceMatcher
import re

import matplotlib.pyplot as plt

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

PATH_TO_FILE = "cleaned_df_FINALISSIMISSIMO_2006_2021.csv"

similarity_songs_list = []
similarity_artists_list = []
avg_similarity = []
songs = []
poor_quality = 0
with open(PATH_TO_FILE) as file_reader:
    reader = csv.reader(file_reader, delimiter=";")
    next(reader)
    for row in reader:
        original_song = re.sub(r"\W+", " ", row[0]).lower()
        original_artist = re.sub(r"\W+", " ", row[1]).lower()
        found_song = re.sub(r"\W+", " ", row[8]).lower()
        found_artist = re.sub(r"\W+", " ", row[10]).lower()

        if original_song not in songs:
            songs.append(original_song)
            similarity_songs=similar(original_song, found_song)
            similarity_songs_list.append(similarity_songs)
            similarity_artists=similar(original_artist, found_artist)
            similarity_artists_list.append(similarity_artists)
            avg_similarity.append((similarity_songs + similarity_artists)/2)

            if similarity_songs < 0.7 or similarity_artists < 0.7:
                poor_quality += 1
                print("\n")
                print(original_song, "|||", found_song, "|||", similarity_songs)
                print(original_artist, "|||",
                      found_artist, "|||", similarity_artists)
                print("\n")

fig, ax = plt.subplots(3,1, sharex=True)
ax[0].hist(similarity_songs_list)

ax[1].hist(similarity_artists_list)

ax[2].hist(avg_similarity)
plt.savefig("Similarity_songs.png", dpi=300)

print(poor_quality)
