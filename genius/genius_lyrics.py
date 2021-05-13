import re
import csv
import os
import lyricsgenius


UNIQUE_SONG_PATH = "./unique_songs.csv"
DOWNLOAD_DIR = "lyrics"


GENIUS_TOKEN = "kkAcDUBp0WMs-dHSKsmGZweB9xLdDBFmXy7NWaWFGBzC0w3HJDMJhNUhihFJns4n"

genius = lyricsgenius.Genius(GENIUS_TOKEN, remove_section_headers=True)


def get_lyrics(song_name, artist_name):
    """
    This function retrieves the songs' lyrics from genius using song_name and artist_name and write them on a txt
    """
    song_lyrics = genius.search_song(song_name, artist_name, get_full_info=True)
    if song_lyrics is not None:
        file = os.path.join(DOWNLOAD_DIR, re.sub(r"[><:\"?*|\\/]", "", f"{song_name}_{artist_name}.txt"))
        file = open(file, "w", encoding="utf-8")
        file.write(song_lyrics.lyrics)
        file.close()
        return True


with open(UNIQUE_SONG_PATH, 'r', encoding="utf-8") as input_handle:
    my_reader = csv.reader(input_handle, delimiter=";")
    header = next(my_reader, None)

    total_saved = 0
    total_not_found = 0
    list_not_found = []
    """
    We search each song on genius using a combination of the columns "original_song_name" and "song_name"
    for the song_name; and the columns "original_artists_name" and "artist_names" for artist_name. 
    In this way we maximize our chances to find the songs lyrics on genius
    """
    for row in my_reader:
        for songs in 1, 3:
            for artists in 2, 4:
                song_name = row[songs]
                artist_name = row[artists]
                lyric = get_lyrics(song_name, artist_name)

                if lyric:
                    total_saved += 1
                    print("Total songs saved: ", total_saved)
                    break

            if lyric:
                break

        if lyric is None:
            total_not_found += 1
            list_not_found.append(song_name + "_" + artist_name)
            print("Total songs not found: ", total_not_found)
            print(list_not_found)


    print("Finished!")
    print("The total songs saved are: ", total_saved)
    print("The total songs not found are: ", total_not_found)
    print("This is the list of the missing songs: ", list_not_found)



with open("list_total_lyrics_not_found.txt", "w", encoding="utf-8") as file1:
    file1.write(list_not_found)









