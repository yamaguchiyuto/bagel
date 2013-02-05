# -*- coding: utf-8 -*-

import json
import sys
import lib.util as util

class SpatialAnalysis:
    def __init__(self, maxdispersion, db):
        self.maxdispersion = maxdispersion 
        self.db = db

    def receive_cluster(self):
        return json.loads(sys.stdin.readline())

    def calc_medoid(self, points):
        centroid = self.calc_centroid(points)
        min_d = -1
        medoid = [-1,-1]
        for p in points:
            d = util.hubeny_distance(p, centroid)
            if d < min_d or min_d == -1:
                min_d = d
                medoid = p
        return medoid

    def calc_centroid(self, points):
        sum_lat = sum([p[0] for p in points])
        sum_long = sum([p[1] for p in points])
        n = float(len(points))
        return [sum_lat/n, sum_long/n]

    def calc_dispersion(self, centroid, points):
        sum_dist = sum([util.hubeny_distance(centroid, p) for p in points])
        n = float(len(points))
        return sum_dist/n

    def output(self, count, cluster):
        output = {
                    'id': count,
                    'tweets':cluster['tweets'],
                    'start': cluster['start'],
                    'end': cluster['end'],
                    'minpts': cluster['minpts'],
                    'eps': cluster['eps'],
                    'maxdispersion': self.maxdispersion,
                    'windowsize': cluster['windowsize']
                    }
        print json.dumps(output)

    def insert(self, count, cluster):
        self.db.insert_event(count, cluster)

    def update_location_distribution(self, cluster):
        pass

    def run(self):
        detected_count = 0
        while True:
            cluster = self.receive_cluster()
            points = [tweet['location'] for tweet in cluster['tweets'] if tweet['location'] != None]
            if len(points) < 2:
                continue

            medoid = self.calc_medoid(points)
            dispersion = self.calc_dispersion(medoid, points)

            if dispersion < self.maxdispersion:
                detected_count += 1
                self.output(detected_count, cluster)
                self.insert_event(detected_count, cluster)
                self.update_location_distribution(cluster)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "[USAGE]: python %s [dispersion threshold]" % sys.argv[0]
        exit()


    maxdispersion = float(sys.argv[1])

    from lib.db import DB
    db = DB()

    sp = SpatialAnalysis(maxdispersion, db)
    sp.run()
