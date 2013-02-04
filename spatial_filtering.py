# -*- coding: utf-8 -*-

import json
import sys
import lib.util as util

class SpatialAnalysis:
    def __init__(self, file, dispersion_threshold):
        self.file = file
        self.dth = dispersion_threshold

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

    def output(self, count, tweets, start_time, end_time, minpts, eps, detected):
        output_value = {'id': count, 'tweets':tweets, 'start':start_time, 'end':end_time, 'minpts':minpts, 'eps':eps, 'detected':detected}
        print json.dumps(output_value)

    def run(self):
        for line in open(self.file, 'r'):
            bursts = json.loads(line.rstrip())
            for burst in bursts['bursts']:
                points = [tweet['location'] for tweet in burst if tweet['location'] != None]
                if len(points) < 2:
                    continue
                medoid = self.calc_medoid(points)
                dispersion = self.calc_dispersion(medoid, points)
                if dispersion < self.dth:
                    detected.append({'prob':p, 'dispersion':dispersion, 'center':centroid})
                    self.output(count, burst, bursts['start'], bursts['end'], bursts['minpts'], bursts['eps'])

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "[USAGE]: python %s [cluster data] [dispersion threshold]" % sys.argv[0]
        exit()

    cluster_file = sys.argv[1]
    dispersion_threshold = float(sys.argv[2])

    sp = SpatialAnalysis(cluster_file, dispersion_threshold)
    sp.run()
