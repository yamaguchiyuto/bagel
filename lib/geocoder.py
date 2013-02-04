#-*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import json

class Geocoder:
	def __init__(self, logging, conf_file, output='json', timeout=2):
                self.logging = logging
		self.url = 'http://geo.search.olp.yahooapis.jp/OpenLocalPlatform/V1/geoCoder'
		self.output = output
		self.api_key = open(conf_file, 'r').readline().rstrip()
		socket.setdefaulttimeout(timeout)

	def _get(self, query):
		while True:
			try:
				params = urllib.urlencode({'output':self.output, 'query':query, 'appid':self.api_key})
				f = urllib2.urlopen(self.url + '?' + params)
				return json.loads(f.read())
			except ValueError, e:
                                self.logging.warning(e)
				return None
			except IOError, e:
                                self.logging.warning(e)
				return None
			except Exception, e:
                                self.logging.warning(e)
				continue

	def get(self, address):
		locations = []
		results = self._get(address)
		if results == None:
			return locations
		if not 'Feature' in results:
			return locations
		for result in results['Feature']:
			long, lat = result['Geometry']['Coordinates'].split(',')
			locations.append({'name':result['Name'], 'lat':lat, 'long':long, 'id': result['Id']})
		return locations
