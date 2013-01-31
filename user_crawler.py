# -*- coding: utf-8 -*-

import sys
import json
import urllib
import socket
import time
import logging

from lib.db import DB

class Crawler:
	def __init__(self, db, logging):
                self.db = db
                self.logging = logging

                self.url = "https://api.twitter.com/1/users/lookup.json"
		socket.setdefaulttimeout(10)

        def output(self, data):
            for user in data:
                self.db.update_user_by_crawled_info(user)

        def error_occurs(self, data):
            if data == None:
                logging.warning("None returned from API")
                return True
            if 'errors' in data:
                # code 34 = All users in DB are collected except not existing users.
                logging.warning(data['errors'])
                return True
            return False
	
	def post(self, params):
		try:
			f = urllib.urlopen(self.url, urllib.urlencode(params))
			data = json.loads(f.read())
			f.close()
                        return data
		except IOError, e:
			logging.warning(e)
                        return None
		except ValueError:
			logging.warning('parse error')
                        return None

	def run(self, uids):
            params = {'user_id': ','.join(uids)}

            data = self.post(params)
            if self.error_occurs(data):
                for uid in uids:
                    db.set_profile_crawled(uid, 2)
                return

            self.output(data)

            crawled_user_count = len(data)
            logging.info("Got %d users", crawled_user_count)


logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='./log/user_crawler.log',
    filemode='w')

db = DB(logging)
crawler = Crawler(db, logging)

while True:
    uids = db.get_crawling_target_user_ids(100)
    if len(uids) == 0:
        logging.info("All users in DB are crwaled, sleep 1 hour")
        time.sleep(60 * 60)
    else:
        crawler.run(uids)

