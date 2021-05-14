import pandas as pd
import random

df = pd.read_csv("../download_df_v2_complete.csv", sep=";")
df["both"] = df["original_song_name"] + " " + df["original_artists_name"]
df = df.groupby("both").first()

indx = list(df.index)
random.shuffle(indx)
sep = len(indx)//5
a, indx = indx[:sep], indx[sep:]
b, indx = indx[:sep], indx[sep:]
c, indx = indx[:sep], indx[sep:]
d, e = indx[:sep], indx[sep:]

df.loc[a].to_csv("a.csv", sep=";", index=False)
df.loc[b].to_csv("b.csv", sep=";", index=False)
df.loc[c].to_csv("c.csv", sep=";", index=False)
df.loc[d].to_csv("d.csv", sep=";", index=False)
df.loc[e].to_csv("e.csv", sep=";", index=False)
