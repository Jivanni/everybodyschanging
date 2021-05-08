import requests
import json
from bs4 import BeautifulSoup

base = "https://api.genius.com"

genius_client_id = "SHaUfi75ySKGfKZvq88nhk53Ki6dlmdZ4ri4-4kZltxLyQ9-IRtOwBkkhiISTmgl"
genius_secret_id = "rZE5J5CB3HHM6AiV5o_y-Iaqz1QbW_M3qqWgmdO01gZ8bJrr-rii0Tjoq9W3qg-VqPmQVsy19Crz40OWxp7F_g"
genius_client_access_token = "kkAcDUBp0WMs-dHSKsmGZweB9xLdDBFmXy7NWaWFGBzC0w3HJDMJhNUhihFJns4n"


def search(artist_name):
    '''Search Genius API via artist name.'''
    search = "search?q="
    query = base + search + urllib.parse.quote(artist_name)
    request = urllib.request.Request(query)

    request.add_header("Authorization", "Bearer " + client_access_token)
    request.add_header("User-Agent", "")

    response = urllib.request.urlopen(request, timeout=3)
    raw = response.read()
    data = json.loads(raw)['response']['hits']

    for item in data:
        # Print the artist and title of each result
        print(item['result']['primary_artist']['name']
              + ': ' + item['result']['title'])


def get_json(path, params=None, headers=None):
    '''Send request and get response in json format.'''

    # Generate request URL
    requrl = '/'.join([base, path])
    token = "Bearer {}".format(genius_client_access_token)
    if headers:
        headers['Authorization'] = token
    else:
        headers = {"Authorization": token}

    # Get response object from querying genius api
    response = requests.get(url=requrl, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def connect_lyrics(song_id):
    '''Constructs the path of song lyrics.'''
    url = "songs/{}".format(song_id)
    data = get_json(url)

    # Gets the path of song lyrics
    path = data['response']['song']['path']

    return path


def retrieve_lyrics(song_id):
    '''Retrieves lyrics from html page.'''
    path = connect_lyrics(song_id)

    URL = "http://genius.com" + path
    print(URL)

    page = requests.get(URL)

    # Extract the page's HTML as a string
    html = BeautifulSoup(page.text, "html.parser")

    # Scrape the song lyrics from the HTML
    lyrics = html.find("div", class_="lyrics").get_text()
    return lyrics


#song_lyrics = [retrieve_lyrics(song_id) for song_id in songs_ids]

song = retrieve_lyrics(16775)

print(song)

