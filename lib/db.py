# -*- coding: utf-8 -*-
import sys
import MySQLdb

import util as util

class DB:
    def __init__(self, logging):
        host, user, passwd, dbname = [entry.rstrip() for entry in open('data/db.conf', 'r').readlines()]
        self.conn = MySQLdb.connect(host, user, passwd, dbname)
        self.cursor = self.conn.cursor()
        self.dict_cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        self.issue_insert('set names utf8')
        self.logging = logging

    # 何もマッチしなければ長さ0のリストを返す
    def issue_insert(self, query):
        try:
            self.cursor.execute(query)
        except Exception, e:
            self.logging.warning(query)
            self.logging.warning(e)

    def issue_select(self, query):
        try:
            self.dict_cursor.execute(query)
            return self.dict_cursor.fetchall()
        except Exception, e:
            self.logging.warning(query)
            self.logging.warning(e)

    def get_tweet(self, tid):
        query = "SELECT * FROM tweets WHERE id = %s" % tid
        return self.issue_select(query)
    def get_tweets(self, n=None):
        if n == None:
            query = "SELECT * FROM tweets WHERE query != '' ORDER BY id"
        else:
            query = "SELECT * FROM tweets WHERE query != '' ORDER BY id LIMIT %s" % n
        return self.issue_select(query)
    
    def get_tweets_with_user(self, uid, n):
        query = "SELECT * FROM tweets WHERE user_id = '%s' LIMIT %d" % (uid, n)
        return self.issue_select(query)

    def get_tweets_with_query(self, q):
        query = "SELECT * FROM tweets WHERE query = '%s' ORDER BY id" % q
        return self.issue_select(query)
    def get_tweets_from_twitterdb(self):
        query = "select * from twitter.tweets where query = '地震' order by id"
        return self.issue_select(query)

    def get_tweets_with_period(self, s, e):
        query = "SELECT * FROM tweets WHERE timestamp BETWEEN '%s' and '%s' ORDER BY id" % (s, e)
        return self.issue_select(query)

    def get_tweet_location(self, tweet_id):
        query = "SELECT locations.id, latitude, longitude from tweets, users, locations where tweets.id = %s and tweets.user_id = users.id and users.location_id = locations.id" % tweet_id
        return self.issue_select(query)
    def get_tweet_location_from_twitterdb(self, tweet_id):
        query = "select l.id, latitude, longitude from twitter.tweets as t, twitter.locations as l, twitter.user_location as ul where t.id = %s and t.user_id = ul.user_id and ul.location_id = l.id;" % tweet_id
        return self.issue_select(query)

    def insert_tweet(self, tweet, q):
        id = tweet['id_str']
        text = util.mysqlescape(tweet['text'])
        user_id = tweet['from_user_id_str']
        timestamp = util.mysqldatetimeformat(tweet['created_at'])
        q = util.mysqlescape(q).decode('UTF-8')
        query = "INSERT INTO tweets VALUES(%s, '%s', %s, '%s', '%s')" % (id, text, user_id, timestamp, q)
        self.issue_insert(query.encode('utf8'))

    def insert_post_user(self, tweet):
        id = tweet['from_user_id_str']
        screen_name = tweet['from_user']
        query = "INSERT INTO users VALUES(%s, '%s', null, -1, -1, -1, -1, null, null, -1)" % (id, screen_name)
        self.issue_insert(query.encode('utf-8'))
    def insert_user_ids(self, uids):
        for uid in uids:
            query = "INSERT INTO users VALUES (%s, null, null, -1, -1, -1, -1, null, null, -1)" % uid
            self.issue_insert(query)

    def update_user_by_crawled_info(self, user):
        id = user['id_str']
        if not user['location'] == None:
            location_property = util.mysqlescape(user['location'])
        else:
            location_property = ""
        name = util.mysqlescape(user['name'])
        query = "UPDATE users SET screen_name = '%s', location_property = '%s', name = '%s', profile_crawled = 1 WHERE id = %s" % (user['screen_name'], location_property, name, id)
        self.issue_insert(query.encode('utf-8'))
    def update_user_by_geocoded_info(self, uid, lid):
        query = "UPDATE users SET location_id = %s, geocoded = 1 WHERE id = %s" % (lid, uid)
        self.issue_insert(query)

    def update_test_users(self, users):
        for u in users:
            query = "UPDATE users SET test_user = 1 WHERE id = %s" % u['id']
            self.issue_insert(query)

    def get_users(self, n):
        query = "SELECT id FROM users WHERE tweets_crawled = -1 LIMIT %s" % n
        uids = self.issue_select(query)
        return [str(uid['id']) for uid in uids]
    def get_test_users(self):
        query = "SELECT id FROM users WHERE test_user = 1"
        uids = self.issue_select(query)
        return [str(uid['id']) for uid in uids]
    def get_test_users_for_cheng(self, n):
        query = "SELECT users.id FROM tweets, users WHERE test_user = 1 and tweets.user_id = users.id group by user_id having count(*) > %d" % n
        uids = self.issue_select(query)
        return [str(uid['id']) for uid in uids]
    def get_crawling_target_user_ids(self, n=100):
        query = "SELECT id FROM users WHERE profile_crawled = -1 LIMIT %d" % n
        uids = self.issue_select(query)
        return [str(uid['id']) for uid in uids]
    def get_crawling_target_test_users(self):
        query = "SELECT id FROM users WHERE test_user = 1 AND tweets_crawled = -1"
        uids = self.issue_select(query)
        return [str(uid['id']) for uid in uids]
    def get_geocoding_target_users(self, n=100):
        query = "SELECT id, location_property FROM users WHERE geocoded = -1 AND profile_crawled = 1 LIMIT %d" % n
        uids = self.issue_select(query)
        return uids
    def get_sg_crawling_target_users(self, n=100):
        query = "SELECT id FROM users WHERE test_user = 1 AND graph_crawled = -1 LIMIT %d" % n
        uids = self.issue_select(query)
        return [str(uid['id']) for uid in uids]
    def get_located_users(self):
        query = "SELECT * FROM users WHERE location_id != -1"
        return self.issue_select(query)


    def get_location(self, lid):
        query = "SELECT * FROM locations WHERE id = %s" % lid
        return self.issue_select(query)
    def insert_location(self, location):
        query = "INSERT INTO locations VALUES (%s, '%s', %s, %s)" % (location['id'], util.mysqlescape(location['name']), location['lat'], location['long'])
        self.issue_insert(query.encode('utf-8'))

    def get_friends(self, uid, n=None):
        if n == None:
            query = "SELECT dst_id FROM social_graph WHERE src_id = %s" % uid
        else:
            query = "SELECT dst_id FROM social_graph WHERE src_id = %s LIMIT %d" % (uid, n)
        uids = self.issue_select(query)
        return [str(uid['dst_id']) for uid in uids]
    def insert_friends(self, uid, friends):
        query = "INSERT INTO social_graph VALUES"
        f = friends.pop(0)
        query += " (%s, %s)" % (uid, f)
        for f in friends:
            query += ", (%s, %s)" % (uid, f)
        self.issue_insert(query)

    def get_user_location(self, uid):
        query = "SELECT location_id, latitude, longitude  FROM users, locations WHERE users.id = %s AND location_id = locations.id" % uid
        result = self.issue_select(query)
        return result

    def set_graph_crawled(self, uid, v):
        query = "UPDATE users SET graph_crawled = %s WHERE id = %s" % (v, uid)
        self.issue_insert(query)
    def set_profile_crawled(self, uid, v):
        query = "UPDATE users SET profile_crawled = %s WHERE id = %s" % (v, uid)
        self.issue_insert(query)
    def set_tweets_crawled(self, uid, v):
        query = "UPDATE users SET tweets_crawled = %s WHERE id = %s" % (v, uid)
        self.issue_insert(query)

    def set_processed(self, tid, v):
        query = "UPDATE twees SET processed = %s WHERE id = %s" % (v, tid)
        self.issue_insert(query)
