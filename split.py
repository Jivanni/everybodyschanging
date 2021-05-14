import pandas as pd

df = pd.read_csv("data/download_df.csv", sep=";")
print(df.shape[0]/5)
