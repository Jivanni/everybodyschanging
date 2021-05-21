"""
Parse the csv row by row to check incongruent data. Return a json/dictionary
where the key are the name and the artist and the value is the spotify id or an
empty string.
"""

from difflib import SequenceMatcher
import csv
import json

CSV_PATH = "/home/giuseppe/Documents/Master/progetto/data/check_data_utils/xaa"
ONLY_GRAPH = True


def apply_sm(str_1: str, str_2: str) -> float:
    """
    Returns the "similarity" between two strings.
    Parameters
    ----------
    str_1 : str
    str_2 :  str

    Returns
    -------
    float
    """
    return SequenceMatcher(None, str_1, str_2).ratio()


redundant_conversion_dict = dict()
with open(CSV_PATH, "r", encoding="utf8") as data_file:
    reader = csv.reader(data_file, delimiter=";")

    for row in reader:
        sm = apply_sm(row[0].lower(), row[8][:len(row[0])].lower())

        if sm < 0.6:
            o_track_name = row[0][:40]
            o_artist_name = row[1][:40]
            f_track_name = row[8][:40]
            f_artist_name = row[10][:40]

            combined_originals = f"{o_track_name} {o_artist_name}"
            if combined_originals not in redundant_conversion_dict:
                print(f"{o_track_name:40}\t{f_track_name:40}\n"
                      f"{o_artist_name:40}\t{f_artist_name:40}")
                new_id = input("Is this valid? ")

                if new_id == "quit!":
                    break
                elif new_id == "???":
                    new_id = "None"

                redundant_conversion_dict[combined_originals] = new_id
                print()
    with open("redundant_conversion.json", "w", encoding="utf8") as outfile:
        json.dump(redundant_conversion_dict, outfile)

    print(f"CONGRATULATIONS! You parsed all alone {len(redundant_conversion_dict)}"
          " songs! Go have a coffee!")
