import lyricsgenius
import csv
import pandas as pd


#Uncomment to create a Csv file with only unique songs

'''
df = pd.read_csv("final_df.csv", delimiter=";", skipinitialspace=True)
df = df.drop_duplicates(['song_id'])
df.to_csv('unique_songs.csv', index=False, header=True, sep=";", encoding="utf-8")
'''


genius_token = "kkAcDUBp0WMs-dHSKsmGZweB9xLdDBFmXy7NWaWFGBzC0w3HJDMJhNUhihFJns4n"


genius = lyricsgenius.Genius(genius_token, remove_section_headers=True)


def get_lyrics(song_name, artist_name):
    song_lyrics = genius.search_song(song_name, artist_name)
    if song_lyrics is not None:
        file = open(f"lyrics/{song_name}_{artist_name}.txt", "w", encoding="utf-8")
        file.write(song_lyrics.lyrics)


with open("unique_songs.csv", 'r', encoding="utf-8") as input_handle:
    my_reader = csv.reader(input_handle, delimiter=";")
    header = next(my_reader, None)

    total_saved = 0
    total_not_found = 0
    list_not_found = []

    # è buggato perché mi scrive i txt dei duplicati

    for row in my_reader:
        try:
            '''
            #i due cicli for con songs e artists li ho messi per provare diverse combinazioni di colonne 
            nel caso in cui non trovi la canzone
            (original_song_name e song_name; original artists name e artist_names).
            Il problema è che non interrompendo il ciclo quando mi trova la canzone, mi scrive i duplicati
            '''

            for songs in 0, 8:
                for artists in 1, 10:
                    song_name = row[songs]
                    artist_name = row[artists]
                    get_lyrics(song_name, artist_name)
                    total_saved += 1


        except:
            list_not_found.append(song_name + "_" + artist_name)
            total_not_found += 1


    print(total_saved)
    print(total_not_found)

    print(list_not_found)