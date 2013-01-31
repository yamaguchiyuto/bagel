import math

class DBSCAN:
    def __init__(self, eps, minpts):
        self.eps = eps
        self.minpts = minpts

    def run(self, data):
        visited = set([])
        noise = set([])
        clusters = []

        for pid, pval in data.items():
            if pid in visited:
                continue
            visited.add(pid)
            seeds = [qid for qid, qval in data.items() if self.distance(pval, qval) < self.eps and pid != qid]
            if len(seeds) < self.minpts:
                noise.add(pid)
            else:
                cluster = [pid]
                while len(seeds) != 0:
                    rid = seeds.pop()
                    if not ( rid in visited ):
                        n = [qid for qid, qval in data.items() if self.distance(data[rid],qval) < self.eps and rid != qid]
                        if len(n) >= self.minpts:
                            seeds += n
                    if not ( rid in visited ) or ( rid in noise ):
                        cluster.append(rid)
                        visited.add(rid)
                        if rid in noise:
                            noise.remove(rid)
                clusters.append(cluster)
        return [clusters, noise]

    def normalize(self, p):
        q = {}
        n = float(sum([1 for v in p]))
        for w in p:
            if not w in q: q[w] = 0
            q[w] += 1/n
        return q

    def distance(self, p, q):
        s = 0
        p = self.normalize(p)
        q = self.normalize(q)
        for k, v in p.items():
            if not k in q: s += v**2
            else: s += (v - q[k])**2
        for k, v in q.items():
            if not k in p: s += v**2
            else: s += (v - q[k])**2
        return math.sqrt(s)

if __name__ == '__main__':
    data = {}
    for i in range(0, 1000):
        data[i] = {1:i, 4:5}
    dbscan = DBSCAN(6.5, 3)
    clusters, noise = dbscan.run(data)
    print clusters
    print noise
