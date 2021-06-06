#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
import re
import csv
import os
import lyricsgenius
import time
from random import randint
from requests.exceptions import Timeout
from tqdm import tqdm


UNIQUE_SONG_PATH = "../../../analysis/lyrics/songlyrics/songs_na_less_5.csv"
DOWNLOAD_DIR = "lyrics"
curr_row = 0

try:
    with open("state.txt", "r", encoding="utf-8") as state:
        curr_row = int(state.readlines()[0])
except FileNotFoundError:
    with open("state.txt", "w", encoding="utf-8") as state:
        state.write("0")

print(f"Resuming from row {curr_row}")

def unpack_artist_list(str_repr):
    output = []
    try:
        output.extend(eval(str_repr))
    except:
        output.append(str_repr)
    finally:
        return output



class Google_scraper:
    def __init__(self):
        # The headers for the Google search used to find the song lyrics
        self.lyricheaders = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en,it;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.artist = None
        self.song = None
        self.query = None
        self.lyrics = ''

    def getlyrics(self):
        # makes a google search for the song playing on the user's account and
        # extracts the song lyrics contained within the page
        self.lyrics = ''
        s = requests.Session()
        url = 'https://www.google.com/search?q={}&ie=utf-8&oe=utf-8'.format(self.query)
        # makes google search
        r = s.get(url, headers=self.lyricheaders)
        # extracts the song lyrics from the Google page
        soup = BeautifulSoup(r.text, "html.parser").find_all("span", {"jsname": "YS01Ge"})
        for link in soup:
            self.lyrics += (link.text + '\n')

    def get_song(self, song, artist):
        self.artist = artist
        self.song = song
        self.query = (str(self.song) + '+' + str(self.artist) + '+lyrics').replace(' ', '+')
        self.getlyrics()

    def save_lyrics(self, clean_filename):
        if self.lyrics:
            path = os.path.join(DOWNLOAD_DIR, clean_filename)
            with open(path, "w", encoding="utf-8") as file_hand:
                file_hand.write(self.lyrics)
            return True
        return False

scraper = Google_scraper()

with open(UNIQUE_SONG_PATH, 'r', encoding="utf-8") as input_handle:
    filelen = sum(1 for line in input_handle)

with open(UNIQUE_SONG_PATH, 'r', encoding="utf-8") as input_handle:
    my_reader = csv.reader(input_handle, delimiter=";")

    for i in range(1,curr_row):
        next(my_reader, None)

    total_saved = 0
    total_not_found = 0
    list_not_found = []
    outer = tqdm(total=filelen - curr_row, desc='Status', position=0)
    inner = tqdm(desc='Getting song:', position=1, bar_format='{desc}')
    for id, song_name, artists_names, song_name_less in my_reader:
        time.sleep(randint(1, 2))
        artists_names = unpack_artist_list(artists_names)
        clean_filename = re.sub(r"[><:\"?*|\\/]", "", f"{song_name}_{artists_names[0]}.txt")
        inner.set_description_str(f"Getting song: {song_name} by {artists_names[0]}")
        outer.update(1)
        lyric = scraper.get_song(song_name_less, artists_names[0])
        scraper.save_lyrics(clean_filename)


    print("Finished!")
    print("The total songs saved are: ", total_saved)
    print("The total songs not found are: ", total_not_found)
    print("This is the list of the missing songs: ", list_not_found)
