# -*- coding: utf-8 -*-

import sys
import json
import logging
import time

import lib.util as util
from lib.db import DB
from lib.grid import Grid

class ContentClustering:
    def __init__(self, window_size, cluster_method, cluster_params, db):
        self.window_size = window_size
        self.cluster_method = cluster_method
        self.cluster_params = cluster_params
        self.stop_words = self.read_stop_words('data/stopwords')
        self.db = db
        self.grid = Grid()

    def read_stop_words(self, file):
        words = {}
        for line in open(file, 'r'):
            word = line.strip()
            words[word] = 1
        return words

    def output(self, start_time, end_time, clusters, buf):
        for c in clusters:
            output = {'start': start_time, 'end': end_time, 'windowsize': self.window_size, 'tweets':[]}
            for k in self.cluster_params:
                output[k] = self.cluster_params[k]
            for tweet_id in c:
                output['tweets'].append({'id': tweet_id, 'words': buf[tweet_id][3], 'text': buf[tweet_id][1], 'location': buf[tweet_id][2], 'user_id': buf[tweet_id][0]})
            print json.dumps(output)
         

    def get_tweets(self, query):
        if query == None:
            return self.db.get_tweets()
        else:
            return self.db.get_tweets_with_query(query)

    def cluster(self, buf):
        cluster_input = {}
        for k in buf:
            cluster_input[k] = buf[k][3]
        clusters, noise = self.cluster_method.run(cluster_input)
        return clusters


    def run(self, query=None):
        buf = {}
        p_time = 0

        for t in self.get_tweets(query):
            """
            get attributes
            """
            tid = t['id']
            text = t['text']
            words = util.get_words_from_tweet(text, self.stop_words)
            location = db.get_tweet_location(tid)
            timestamp = time.mktime(util.encode_mysql_datetime_format("%s" % t['timestamp']))

            if len(location) == 0:
                location = None
            else:
                location = [location[0]['latitude'], location[0]['longitude']]
            buf[tid] = (t['user_id'], text, location, words)

            self.db.set_processed(tid, 1)

            if p_time + self.window_size < timestamp:
                """
                clustering
                """
                clusters = self.cluster(buf)
                if not len(clusters) == 0:
                    self.output(p_time, timestamp, clusters, buf)

                """
                for next window
                """
                buf = {}
                p_time = timestamp

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "[USAGE]: python content_clustering.py [window size] [minpts] [eps] (query)" % sys.argv
        exit()

    from lib.dbscan import DBSCAN

    window = int(sys.argv[1])
    minpts = int(sys.argv[2])
    eps = float(sys.argv[3])
    if len(sys.argv) == 5:
        query = sys.argv[4]
    else:
        query = None

    db = DB(logging)
    cluster_method = DBSCAN(eps, minpts)
    cc = ContentClustering(window, cluster_method, {'minpts': minpts, 'eps':eps}, db)
    cc.run(query)
