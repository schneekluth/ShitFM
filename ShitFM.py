#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from prettytable import PrettyTable
import urllib2
import itertools 
import csv

def initial_Scrape():
	## Fetches Metadata from url
	url_initial = "http://www.ndr.de/ndr2/programm/titelliste1202.html"
	request = urllib2.Request(url_initial)
	request.add_header('User-agent', 'Mozilla 5.10')
	response = urllib2.urlopen(request)
	html = response.read()
	response.close()
	
	#print "NDR2 PLAYLIST >> SCRAPING METADATA\n"
	soup = BeautifulSoup(html)
	rundates = soup.find("select", attrs={"id": "date"}).findAll("option")
	run_Times = soup.find("select", attrs={"id":"timeselect"}).findAll("option")
	current_selected_date = soup.find("select", attrs={"id": "date"}).find("option",{"selected":"selected"})["value"]#.text
	current_selected_time = soup.find("select", attrs={"id":"timeselect"}).find("option",{"selected":"selected"}).text

	## Find available Dates to scrape in format YYYY-MM-DD and store them in an array
	#  Format: e.g.: [2014-11-23, ?date=2014-11-23]
	array_Dates_Meta = [] 
	array_Dates_URL = []

	for day in rundates:
		#print day["value"]
		array_Dates_Meta.append(day["value"])
		array_Dates_URL.append("?date=" + day["value"])
		#array_Dates.append([day["value"], "?date=" + day["value"]])

	## Find running times and store them in array
	#  Format: e.g.: [[01, 01:00 - 02:00, &hour01]] 
	array_Times_Meta = []
	array_Times_URL = []

	for runtime in run_Times:
		array_Times_Meta.append(runtime.text)
		array_Times_URL.append("&hour=" + runtime["value"])

	# PRINTING
	# print "Curr. selected  >>  DATE: " + current_selected_date
	# print "                    TIME: " + current_selected_time + "\n"
	# print "Avail. Dates    >>  FROM: " + array_Dates_Meta[-1]
	# print "                    TILL: " + array_Dates_Meta[0] + "\n"
	
	return html, array_Dates_Meta, array_Times_Meta, array_Dates_URL, array_Times_URL

def generate_URLS():
	## Returns a dictionary with formated urls ready to scrape
	url_prefix = "http://www.ndr.de/ndr2/programm/titelliste1202.html"
	url_suffix = "&search_submit=Anzeigen"

	variants = list(itertools.product(reversed(array_Dates_URL), array_Times_URL))
	url_prefix = "http://www.ndr.de/ndr2/programm/titelliste1202.html"
	url_suffix = "&search_submit=Anzeigen"
	array_url_mid = []
	urls_final = []

	## for all variants join both strings to one string e.g.: ?date=2014-11-18&hour=03
	for i in variants :
		array_url_mid.append("".join(i))

	## Generating list of scrapeable urls
	for url_middle in array_url_mid :
		urls_final.append(url_prefix + url_middle + url_suffix)
	#print urls_final[1]

	return urls_final	

def Scrape(url):
	## Fetches Metadata from url
	request = urllib2.Request(url)
	request.add_header('User-agent', 'Mozilla 5.10')
	response = urllib2.urlopen(request)
	html = response.read()
	response.close()
	soup = BeautifulSoup(html)	## creating BeautifulSoup Object

	x = PrettyTable(["DATE", "TIME", "ARTIST", "SONG"])
	x.padding_width = 1
	x.border = True # Rahmen 
	x.header = False # Kopfzeile
	x.align["DATE"] = "c"
	x.align["TIME"] = "c"
	x.align["ARTIST"] = "l"
	x.align["SONG"] = "l"
	#table.min_width["ARTIST"] = 30
	#x.sortby = "TIME" # Sorting table 

	# Entries in Playlist
	playlist = soup.find("div", {"id": "playlist"}).findAll("li",{"class":"program"})
	Date = soup.find("select", attrs={"id": "date"}).find("option",{"selected":"selected"}).text
	## Find data in playlist entries
	for entry in playlist:
		Time = entry.find("div", {"class":"timeandplay"}).text
		Artist = entry.find('h3').find("span", {"class":"artist"}).text
		Title = entry.find('h3').find("span", {"class":"title"}).text
		test_print = Date, Time, Artist, Title
		test = Date, Time, Artist, Title, Date, Time
		#print "\t".join(test).encode('ascii', 'ignore')
		## Create and add Time, Artist, Title to file
		f = open("playlist.txt","a")
		f.write("\t".join(test).encode("utf-8") + "\n")
		f.close()
		x.add_row([Date, Time, Artist, Title])
		#print "\t".join(test_print).encode("utf-8")
		#print Date.encode("utf-8") + "   " + Time.encode("utf-8") + "    " + Artist.encode("utf-8") + "\t\t" + Title.encode("utf-8")
		print x

# PROGRAMM START

# Fetch Metadata and already url-formatted data from function: initial_Scrape()
html, array_Dates_Meta, array_Times_Meta, array_Dates_URL, array_Times_URL = initial_Scrape()

# Generate URLs from Metadata
urls_final = generate_URLS()

# Pass URLs to Scraper
print ">>> SCRAPING URLs"
for url in urls_final:
	Scrape(url)

# Convert Data from Scrape(url) to .csv-file using python-csv
txt_file = r"playlist.txt"
csv_file = r"playlist.csv"
in_txt = csv.reader(open(txt_file, "rb"), delimiter = '\t')
out_csv = csv.writer(open(csv_file, 'wb'))
out_csv.writerows(in_txt)
print ">>> Saving playlist.csv SUCCESSFUL."

# Convert playlist.csv to JSON
fieldnames=["Date","Time","Artist","Song"]
csv_filename = "playlist.csv"
print "   Opening CSV file: >>",csv_filename
f=open(csv_filename, 'r')
csv_reader = csv.DictReader(f,fieldnames)
json_filename = csv_filename.split(".")[0]+".json"
print "Saving JSON to file: >>",json_filename
jsonf = open(json_filename,'w')
data = json.dumps([r for r in csv_reader])
jsonf.write(data)
f.close()
jsonf.close()
print ">>> Saving playlist.json SUCCESSFUL."

print "\n FINISHED PRINTING SCRAPE DATA\n"