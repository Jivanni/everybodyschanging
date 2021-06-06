import re
import pandas as pd
import requests
import os
import json
import time
from tqdm import tqdm

ROOT = "https://musicbrainz.org/ws/2/artist?"
LOOKUP = "https://musicbrainz.org/ws/2/artist/"
params = {
    "query" : "",
    "limit" : "1",
    "fmt" : "json"
}
params_search = {
    "inc" : "aliases+recordings+releases+release-groups+works+annotation+tags+ratings+genres+area-rels+artist-rels+event-rels+instrument-rels+label-rels+place-rels+recording-rels+release-rels+release-group-rels+series-rels+url-rels+work-rels",
    "fmt" : "json"
}

DOWNLOAD_DIR = "downloads"
JSONS = "artist_jsons"

BRAINZ_SESSION = requests.Session()
LOOKUP_SESSION = requests.Session()

REG = re.compile(r"[\/\"\\]")

try:
    download_path = os.path.join(DOWNLOAD_DIR, JSONS)
    os.makedirs(download_path)
except FileExistsError:
    pass

def artist_search(artist):
    params.update({"query" : artist})
    resp = BRAINZ_SESSION.get(url=ROOT, params=params)
    data = resp.json()
    firstmatch = None
    try:
        firstmatch = data["artists"][0]
    except:
        return firstmatch
    return firstmatch

def artist_lookup(json):
    resp = LOOKUP_SESSION.get(url=LOOKUP+json["id"]+"?", params=params_search)
    data = resp.json()
    return data

artists_list = pd.read_csv("nas.csv", sep = ";")


outer = tqdm(total=artists_list.size , desc='Status', position=0)
inner = tqdm(desc='Getting artist:', position=1, bar_format='{desc}')

for artist in artists_list["artists_names"]:
    time.sleep(2)
    search_result = artist_search(artist)
    if search_result:
        json_data = artist_lookup(search_result)
        clean_filename = re.sub(r"[><:\"?*|\\/]", "",  f'{artist}.json')
        outer.update(1)
        with open(os.path.join(download_path,clean_filename), 'w') as outfile:
            json.dump(json_data, outfile)
        try:
            inner.set_description_str(f"found artist: {artist}, site_name: {json_data['name']}, country: {json_data['country']}")
        except:
            inner.set_description_str(f"found artist or group : {artist}")
    else:
        inner.set_description_str(f"artist {artist} not found")

LOOKUP_SESSION.close()
BRAINZ_SESSION.close()


