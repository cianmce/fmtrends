from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import os

MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost/fmtrends')
MONGODB_URI = 'mongodb://heroku_gxwl3h33:74h20f9q3ksecnsi3n4dm3p01g@ds055852.mlab.com:55852/heroku_gxwl3h33'
print 'MONGODB_URI:',MONGODB_URI
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client.get_default_database()

def play_near(play, plays):
    minutes = 150
    for p in plays:
        d = (p['played_at'] - play['played_at']).total_seconds()
        if 0 < d and d < (minutes * 60) and p['_id'] is not play['_id']:
            # delete p
            q = {
                '_id': p['_id']
            }
            # print '\n\n'
            # print db.plays.remove(q)
            print play
            print d
            print p
            
            # print '\n\n'


def main():
    tracks = db.tracks.find({
            'count': {
                '$gt': 1
            }
        })

    for track in tracks[:]:
        plays = db.plays.find({
                'track_id': track['_id']
            })
        # print track
        plays = list(plays)
        for play in plays:
            d = play['played_at'] - plays[0]['played_at']
            play_near(play, plays)

if __name__ == '__main__':
    main()
