import webapp2
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from google.appengine.api import mail
import re

import sys
sys.path.insert(0,'libs')

from bs4 import BeautifulSoup

class Offer(ndb.Model):
	code = ndb.IntegerProperty(indexed=True)
	link = ndb.StringProperty(indexed=False)
	price = ndb.IntegerProperty(indexed=False)
	address = ndb.StringProperty(indexed=False)
	art = ndb.StringProperty(indexed=True)
	roomNumber = ndb.FloatProperty(indexed=True)
	square = ndb.FloatProperty(indexed=True)
	timestamp = ndb.DateTimeProperty(auto_now_add=True,indexed=True)

	def __str__(self):
		return str(self.code)

	def __eq__(self, other): 
		return self.code == other.code

	def __hash__(self):
		return hash(self.code)

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.write('Hello, World!')

		self.fetchPage("http://www.studentenwerk-muenchen.de/wohnen/vermittlung-von-privatzimmern/angebote/")

	def fetchPage(self, url):
		r  =  urlfetch.fetch(url)
		data = r.content
		soup = BeautifulSoup(data)

		for link in soup.find_all("tr", class_="tx_stwmprivatzimmervermittlung_list"):
			#get code and check if its already in db
			code = int(link.findNext("td", class_="angebotsnummer").findNext("a").text)
			if not self.offerExists(code):
				offer = Offer()
				offer.code = code
				offer.link = self.trimSpaces("http://www.studentenwerk-muenchen.de/" + link.findNext("td", class_="angebotsnummer").findNext("a")['href'])
				offer.price = int(re.findall(r'\D*([0-9,.]+)\D*', self.trimSpaces(link.findNext("td", class_="miete ").text))[0].replace(',', '').replace('.', ''))
				offer.address = self.trimSpaces(link.findNext("td", class_="strasse ").text)
				offer.art = self.trimSpaces(link.findNext("td", class_="zimmerart ").text)
				offer.roomNumber = float(self.trimSpaces(link.findNext("td", class_="anzahl ").text))
				offer.square = float(self.trimSpaces(link.findNext("td", class_="groesse ").text))
				offer.put()

				self.response.write('Offer saved: ' + offer.code)

				mail.send_mail("gremoz@gmail.com", "gremoz@gmail.com", "New appartments", offer.link)

	def offerExists(self, code):
		offer_query = Offer.query(Offer.code == code)
		count = len(offer_query.fetch(keys_only=True))
		return (count > 0)

	def trimSpaces(self, str):
		cleanStr = ' '.join(str.split())
		try:
			return unicode(cleanStr, 'utf-8').encode("utf-8")
		except TypeError:
			return cleanStr.encode('utf-8')

application = webapp2.WSGIApplication([('/', MainPage),], debug=True)