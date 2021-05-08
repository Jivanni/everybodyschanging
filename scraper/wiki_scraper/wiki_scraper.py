import tagme
import re
import pandas as pd

artists = pd.read_csv("unique_songs.csv", sep=";")
out = []
for auths in artists["artists"]:
    artists_split = re.split(r"feat.|,|&|/", auths)
    for artist in artists_split:
        query = tagme.query_tagme(artist)["annotations"]
        if len(query) > 0:
            out.append(query[0]["title"])
        else:
            out.append("none")