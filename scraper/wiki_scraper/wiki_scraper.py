import tagme
import re
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import json

DOWNLOAD_DIR = "downloads"
HTMLS = "artist_pages"

ENDPOINT = "https://swat.d4science.org/salience" #"https://tagme.d4science.org/tagme/tag"
LANG = "it"
# TODO: inserisci qui il tuo token
KEY = "56cd67a3-c4cc-48dd-9ecb-c20c0c31208f-843339462"

def query_swat(text):
	payload = json.dumps({"title": text, "content": text})
	r = requests.post(ENDPOINT, data=payload, params = {'gcube-token': KEY})
	if r.status_code != 200:
		raise Exception("Error on text: {}\n{}".format(text, r.text))
	return r.json()


try:
    download_path = os.path.join(DOWNLOAD_DIR, HTMLS)
    os.makedirs(download_path)
except FileExistsError:
    pass
LANG = "it"
WIKI_URL = f"https://{LANG}.wikipedia.org/wiki/"

def get_html(url: str) -> BeautifulSoup:
    """
    This function retrieves an html file given an url
    Parameters
    ----------
    url : str
    url of the page to download

    Returns
    -------
    BeautifulSoup() object
    """
    doc = requests.get(url)
    doc.raise_for_status()
    return doc.text #BeautifulSoup(doc.text, 'html.parser')


artists = pd.read_csv("unique_songs.csv", sep=";")
out = []
for auths in artists["artists"]:
    artists_split = re.split(r"feat.|,|&|/", auths)
    for artist in artists_split:
        query = tagme.query_swat(artist)["annotations"]
        if len(query) > 0:
            artist_name = query[0]["title"]
            with open(download_path+"/"+artist_name+".html", "w", encoding='utf-8') as page:
                page.write(str(get_html(WIKI_URL+artist_name)))

