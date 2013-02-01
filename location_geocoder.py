import sys
import logging
import time

from lib.geocoder import Geocoder
from lib.db import DB


logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='./log/location_geocoder.log',
    filemode='w')

geocoder = Geocoder(logging)
db = DB(logging)

while True:
    users = db.get_geocoding_target_users(100)
    for user in users:
        if user['location_property'] == '':
            db.update_user_by_geocoded_info(user['id'], -1)
            logging.info("Cannot geocoded %s", user['id'])
            time.sleep(10)
            continue
        locations = geocoder.get(user['location_property'])
        if len(locations) == 0:
            db.update_user_by_geocoded_info(user['id'], -1)
            logging.info("Cannot geocoded %s", user['id'])
            time.sleep(10)
            continue
        location = locations.pop(0)
        location['id'] = location['id'].split('.')[0]

        db.insert_location(location)
        db.update_user_by_geocoded_info(user['id'], location['id'])
        logging.info("Geocoded %s", user['id'])
