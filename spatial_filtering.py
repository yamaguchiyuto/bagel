# -*- coding: utf-8 -*-

import json
import sys
import lib.util as util

class SpatialAnalysis:
    def __init__(self, cluster_file, maxdispersion):
        self.cluster_file = cluster_file
        self.maxdispersion = maxdispersion 

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

    def run(self):
        detected_count = 0
        for line in open(self.cluster_file, 'r'):
            cluster = json.loads(line.rstrip())
            points = [tweet['location'] for tweet in cluster['tweets'] if tweet['location'] != None]
            if len(points) < 2:
                continue

            medoid = self.calc_medoid(points)
            dispersion = self.calc_dispersion(medoid, points)

            if dispersion < self.maxdispersion:
                detected_count += 1
                self.output(detected_count, cluster)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "[USAGE]: python %s [cluster data] [dispersion threshold]" % sys.argv[0]
        exit()

    cluster_file = sys.argv[1]
    dispersion_threshold = float(sys.argv[2])

    sp = SpatialAnalysis(cluster_file, dispersion_threshold)
    sp.run()
