# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from optparse import OptionParser

import requests
from time import gmtime, strftime
import csv

class Offer:
	def __init__(self, code, link, price, address, art, roomNumber, square, timestamp=None):
		self.code = self.trimSpaces(code) #parse int to remove all \s-paces
		self.link = self.trimSpaces(link)
		self.price = self.trimSpaces(price)
		self.address = self.trimSpaces(address)
		self.art = self.trimSpaces(art)
		self.roomNumber = self.trimSpaces(roomNumber)
		self.square = self.trimSpaces(square)

		if timestamp is None:
			self.timestamp = self.trimSpaces(strftime("%d-%m-%Y %H:%M:%S", gmtime()))
		else:
			self.timestamp = self.trimSpaces(timestamp)


	def __str__(self):
		return self.code 

	def trimSpaces(self, str):
		try:
			encStr = unicode(str, 'utf-8').encode("utf-8")
		except TypeError:
			encStr = str.encode('utf-8')

		return ' '.join(encStr.split())

	def __eq__(self, other): 
		return self.code == other.code

	def __hash__(self):
		return hash(self.code)

def getOffersFromCSVFile(path):
	offers = set()
	inputFileDescriptor = open(path, "rU")
	reader = csv.reader(inputFileDescriptor, delimiter=';', quoting=csv.QUOTE_MINIMAL)
	for row in reader:
		offers.add(Offer(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

	inputFileDescriptor.close();

	return offers

def main():
	"""
	Usage:
		watcher.py [path to content file]

	"""
	usage = "watcher.py [path to content file]"
	parser = OptionParser(usage)
	(options, args) = parser.parse_args()

	if len(args) != 1:
		parser.print_usage()
		sys.exit(1)

	r  = requests.get("http://www.studentenwerk-muenchen.de/wohnen/vermittlung-von-privatzimmern/angebote/")
	data = r.text
	soup = BeautifulSoup(data)
	#get existing offers
	localOffers = getOffersFromCSVFile(args[0])

	fetchedOffers = set()

	for link in soup.find_all("tr", class_="tx_stwmprivatzimmervermittlung_list"):
		fetchedOffers.add(Offer( \
		link.findNext("td", class_="angebotsnummer").findNext("a").text, \
		"http://www.studentenwerk-muenchen.de/" + link.findNext("td", class_="angebotsnummer").findNext("a")['href'], \
		link.findNext("td", class_="miete ").text, \
		link.findNext("td", class_="strasse ").text, \
		link.findNext("td", class_="zimmerart ").text, \
		link.findNext("td", class_="anzahl ").text, \
		link.findNext("td", class_="groesse ").text))

	newOffers = fetchedOffers - localOffers
	obsoleteOffers = localOffers - fetchedOffers

	outputFileDescriptor = open(args[0], "w")
	writer = csv.writer(outputFileDescriptor, delimiter=';', quoting=csv.QUOTE_MINIMAL)

	for offer in (localOffers - obsoleteOffers).union(newOffers):
		writer.writerow([offer.code, offer.link, offer.price, offer.address, offer.art, offer.roomNumber, offer.square, offer.timestamp])

	outputFileDescriptor.close()

	for o in newOffers:
		print o.link

if  __name__ =='__main__':main()

