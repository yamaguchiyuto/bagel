# -*- coding: utf-8 -*-

import sys
import json
import urllib
import socket
import time
import logging

from lib.db import DB

class Crawler:
	def __init__(self, db, query, logging):
                self.db = db
                self.query = query
                self.logging = logging

		self.rpp = 100 # number of tweets per page
		self.n_max = 1000 # number of tweets per one request URL
                self.url = "https://search.twitter.com/search.json"
		socket.setdefaulttimeout(10)

        def output(self, data):
            for tweet in data['results']:
                self.db.insert_tweet(tweet, self.query)
                self.db.insert_post_user(tweet)

        def get_max_and_min_id(self, data, max_id, min_id):
            for tweet in data['results']:
                if max_id > tweet['id']:
                    max_id = tweet['id']
                if min_id < tweet['id']:
                    min_id = tweet['id']
            return [max_id, min_id]

	def get(self, params):
		try:
			f = urllib.urlopen(self.url + '?' + urllib.urlencode(params))
			data = json.loads(f.read())
			f.close()
                        return data
		except IOError, e:
			logging.warning(e)
                        return None
		except ValueError:
			logging.warning('parse error')
                        return None

        def error_check(self, data):
            if 'errors' in data:
                return data['errors'][0]['code']
            elif 'error' in data:
                return -1
            else:
                return None

	def run(self, min_id=0):
            logging.info("query: %s", self.query)
            params = {'q': self.query, 'result_type': 'recent', 'rpp': self.rpp, 'include_entities': 'true', 'since_id': min_id}
            max_id = float('inf')
            while 1:
                p = 1
                logging.info("[%s] <= [%s]", min_id, max_id)
                while 1:
                    params['page'] = p
                    data = self.get(params)

                    """
                    Error handling
                    """
                    error_code = self.error_check(data)
                    if error_code == 130:
                        logging.info('Over capasity: sleep 1 minute')
                        time.sleep(60)
                        continue
                    elif error_code != None:
                        logging.info(data['errors'])
                        exit()

                    self.output(data)
                    max_id, min_id = self.get_max_and_min_id(data, max_id, min_id)

                    # logging crawling statuses
                    crawled_tweets = len(data['results'])
                    logging.info("page %d : %d tweets are crawled", p, crawled_tweets)

                    # update for next loop
                    p = p + 1
                    if p > self.n_max / self.rpp:
                        break

                if 'max_id' in params and params['max_id'] == max_id:
                    break
                params['max_id'] = max_id
            return min_id

if len(sys.argv) < 2:
	print "USAGE: python %s [query]"
	print "query: 'IBM AND Apple'"
	print "query: 'IBM OR Apple'"
	exit()

query = sys.argv[1]

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='./log/tweet_crawler.log',
    filemode='w')

db = DB(logging)
crawler = Crawler(db, query, logging)

min_id = 0
while True:
    min_id = crawler.run(min_id)
    logging.info("Sleep 3 hours")
    time.sleep(60 * 60 * 3)
