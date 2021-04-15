from bs4 import BeautifulSoup
import requests
import csv
from datetime import date, datetime, timedelta
import os

CHART_CODE = 18
CHART_NAME = "italy_top_20"
URL = f"https://top40-charts.com/chart.php?cid={CHART_CODE}&date="
START_DATE = '2018-11-15'
END_DATE = '2021-04-01'
DOWNLOAD_DIR = "downloads"
FIELD_NAMES = ["rank", "title", "artist"]
global next_date

def get_html(url):
	doc = requests.get(url)
	doc.raise_for_status()
	return BeautifulSoup(doc.text, 'html.parser')

def get_songs(soup):
	songs = soup.find_all("tr", class_="latc_song")
	global next_date
	next_date = soup.find("a", string="Next")["href"][-10:]
	out = []
	for s in songs:
		data = s.find_all(text=True)
		out.append([data[0], data[2], data[3]])
	return out

try:
	os.mkdir(DOWNLOAD_DIR + "/" + CHART_NAME)
except FileExistsError:
	pass

curr = START_DATE
end = date.fromisoformat(END_DATE)

while date.fromisoformat(curr) <= end:
	chart_url = URL + curr
	csv_filename = DOWNLOAD_DIR + "/" + CHART_NAME + "/" + curr + "_" + CHART_NAME + ".csv"
	html = get_html(chart_url)
	data = get_songs(html)
	with open(csv_filename, "w", newline='', encoding='utf-8') as file_handler:
		writer = csv.writer(file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		writer.writerow(FIELD_NAMES)
		for song in data:
			writer.writerow([song[0], song[1], song[2]])
			print(song)
	print(curr)
	with open("log.txt", "a+") as logfile:
		logfile.write("\n" + curr)
	curr = next_date
