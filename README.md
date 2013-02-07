REQUIRED CONFIGURE FILES:
	data/db.conf
	data/geocoder.conf
	data/stopwords

> cat data/db.conf
host
user
passwd
dbname

> cat data/geocoder.conf
API key

> cat data/stopwords
stopword1
stopword2
stopword3
stopword4
...



HOW TO START:
	mysql -u [username] -p [dbname] < dump/bagel.sql	# Restore tables without data
	python tweet_crawler.py 'QUERY1 OR QUERY2'		# Start tweet crawler; specify query keywords
	python user_crawler.py 					# Start user crawler
	python location_geocoer.py				# Start location geocoder; this requires data/geocoder.conf
	python content_clustering.py [windowsize in seconds] [minpts] [eps] '[query]' | python spatial_filtering.py [maxdispersion] > output_file.json


Tables in Bagel DB:
	tweets
		crawled tweets
	users
		crawled users
	locations
		crawled locations
	events
		detected events
	location_distribution
		inferred location distribution
	event_tweets
		tweets assignments to events



Cluster output format:
{
	'start': 10000000.0,
	'end': 10000010.0,
	'windowsize': 600,
	'eps': 0.2,
	'minpts': 15
	'tweets': [
			{
				'id': 1,
				'user_id': 1,
				'location_id': 1,
				'location': [35.0, 135.0],
				'text': 'hello world',
				'words': ['hello', 'world']
			},
			{
				'id': 2,
				'user_id': 2,
				'location_id': 1,
				'location': [35.0, 135.0],
				'text': 'earthquake !!!',
				'words': ['earthquake', '!!!']
			}
		  ]
	
}

Event output format:
{
	'id': 1,
	'start': 1000000.0,
	'end': 1000010.0,
	'windowsize': 600,
	'eps': 0.2,
	'minpts': 15,
	'maxdispersion': 200000,
	'center': [35.0, 135.0],
	'tweets': [
		{
			'id': 1,
			'user_id': 1,
			'location_id': 1,
			'location': [35.0, 135.0],
			'text': 'hello world',
			'words': ['hello', 'world']
		},
		{
			'id': 2,
			'user_id': 2,
			'location_id': 1,
			'location': [35.0, 135.0],
			'text': 'earthquake !!!',
			'words': ['earthquake', '!!!']
		}
	  ]
}
