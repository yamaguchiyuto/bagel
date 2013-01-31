# -*- coding: utf-8 -*-
import time
import re
import MeCab
import math

tagger = MeCab.Tagger("-Ochasen")

def mysqlescape(text):
    return text.replace('\n', ' ').replace('\t', ' ').replace('\\', '\\\\').replace("'", "\\'").replace(',', '[COMMA]').replace('"', '\\"')

def encode_twitter_format_time(text):
    return time.strptime(text, "%a, %d %b %Y %H:%M:%S +0000")

def encode_twitter_format_time2(text):
    return time.strptime(text, "%a %b %d %H:%M:%S +0000 %Y")
    #Thu Nov 01 05:05:40 +0000 2012

def encode_mysql_datetime_format(text):
    return time.strptime(text, "%Y-%m-%d %H:%M:%S")
def decode_mysql_datetime_format_from_unixtime(t):
    struct_time = time.gmtime(t)
    return decode_mysql_datetime_format(struct_time)
def decode_mysql_datetime_format(struct_time):
    return time.strftime("%Y-%m-%d %H:%M:%S", struct_time)
def mysqldatetimeformat(text):
    t = encode_twitter_format_time(text)
    return decode_mysql_datetime_format(t)
def mysqldatetimeformat2(text):
    t = encode_twitter_format_time2(text)
    return decode_mysql_datetime_format(t)

def get_words_from_tweet(text, stopwords={}):
    words = []
    node = tagger.parseToNode(remove_usernames_and_urls(text))
    while node:
        if node.feature.split(',')[0] == '名詞' and not node.surface in stopwords:
            words.append(node.surface)
        node = node.next
    return words

def is_retweet(text):
    if re.search("^RT @\w+:", text) == None:
        return False
    else:
        return True

def remove_usernames_and_urls(text):
    username_removed_text = re.sub('@\w+', '', text) # remove usernames
    return re.sub('(https?|ftp)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)', '', username_removed_text) # remove urls

def rad(x):
    return x * math.pi / 180

def hubeny_distance(p, q):
    latd = rad(p[0] - q[0])
    longd = rad(p[1] - q[1])
    latm = rad(p[0] + q[0]) / 2
    a = 6377397.155
    b = 6356079.000
    e2 = 0.00667436061028297
    W = math.sqrt(1 - e2 * math.sin(latm)**2)
    M = 6334832.10663254 / W**3
    N = a / W
    d = math.sqrt((latd*M)**2 + (longd*N*math.cos(latm))**2)
    return d

def norm(p):
    q = {}
    n = float(sum([v for k, v in p.items()]))
    for k, v in p.items():
       q[k] = v/n 

    return q


def kl_divergence(p, q):
    p = norm(p)
    q = norm(q)
    kl = 0
    for k, v in p.items():
        kl += v * math.log(v / q[k])
    return kl

def calc_medoid(points):
    centroid = calc_centroid(points)
    min_d = -1
    medoid = [-1,-1]
    for p in points:
        d = hubeny_distance(p, centroid)
        if d < min_d or min_d == -1:
            min_d = d
            medoid = p
    return medoid

def calc_centroid(points):
    sum_lat = sum([p[0] for p in points])
    sum_long = sum([p[1] for p in points])
    n = float(len(points))
    return [sum_lat/n, sum_long/n]

def calc_dispersion(centroid, points):
    sum_dist = sum([hubeny_distance(centroid, p) for p in points])
    n = float(len(points))
    return sum_dist/n



