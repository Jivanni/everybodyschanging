import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.animation as anim
import seaborn as sns
sns.set_theme(context="paper", style="whitegrid", palette="Paired_r")

from sklearn.manifold import TSNE

REPRESENTATION_CSV_PATH = "/home/giuseppe/Documents/Master/progetto/analysis/music" \
                          "/outpu_encoder.csv"
CHART_DATA_PATH = "/home/giuseppe/Documents/Master/progetto/data/cleaned_df_v2.csv"

print("Loading CSVs")
representations_df = pd.read_csv(REPRESENTATION_CSV_PATH)

chart_df = pd.read_csv(CHART_DATA_PATH, sep=";")
chart_df["date_chart"] = pd.to_datetime(chart_df["date_chart"],
                                        format="%Y-%m-%d")
print("Preprocessing the data")
ids_in_chart = pd.unique(chart_df["id"])
mask = representations_df["song_id"].isin(ids_in_chart)
representations_df = representations_df[mask]

columns_from_neurons = [
    col
    for col in representations_df.columns
    if col != "song_id"
]

print("Doing TSNE")
pure_data = representations_df[columns_from_neurons]
embedded_data = TSNE(n_components=2, n_jobs=-1).fit_transform(pure_data)
embedded_data = pd.DataFrame(embedded_data,
                             columns=["TSNE1", "TSNE2"])
embedded_data["id"] = representations_df["song_id"]

resampled_chart = chart_df.set_index("date_chart").resample("M")
grouped_list = list(resampled_chart)

print("Animation")
fig, ax = plt.subplots(dpi=300)

fig.set_tight_layout(True)
ax.grid(True)
ax.axis("off")


def update(i):
    ax.cla()
    label, df = grouped_list[i]
    label = label.strftime("%B-%Y")
    ax.scatter(embedded_data["TSNE1"], embedded_data["TSNE2"],
               label="everything",
               s=3)
    ax.set_title(label)

    df = df.merge(embedded_data, on=["id", "id"])

    return ax.scatter(df["TSNE1"], df["TSNE2"], label="current_year",
                      s=5)

tsne_anim = FuncAnimation(fig, func=update,
                          interval=300, frames=list(range(len(grouped_list))))
ax.legend()
plt.show()
#writergif = anim.PillowWriter(fps=30)
#tsne_anim.save("~/Desktop/animation.gif", writer=writergif)
