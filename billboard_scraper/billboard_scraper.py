import billboard
import csv
from datetime import date
import os

#requires https://github.com/guoguo12/billboard-charts

CHART_NAME = 'billboard-200'
START_DATE = '2020-01-01'
END_DATE = '2020-06-28' #starts downloading weekly charts from END_DATE backwards to START_DATE
DOWNLOAD_DIR = "downloads"
FIELD_NAMES = ["rank", "title", "artist"]

start = date.fromisoformat(START_DATE)
curr = END_DATE

try:
	os.mkdir(DOWNLOAD_DIR + "/" + CHART_NAME)
except FileExistsError:
	pass

while date.fromisoformat(curr) >= start:
	curr_chart = billboard.ChartData(CHART_NAME, curr)
	csv_filename = DOWNLOAD_DIR + "/" + CHART_NAME + "/" + curr + "_" + CHART_NAME + ".csv"

	with open(csv_filename, "w", newline='') as file_handler:
		writer = csv.writer(file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		writer.writerow(FIELD_NAMES)
		for song in curr_chart:
			writer.writerow(
				[song.rank, song.title, song.artist]
			)
	print(curr)
	with open("log.txt", "a+") as logfile:
		logfile.write("\n" + curr)
	curr = curr_chart.previousDate

print("finished")



