"""
API key 1dda66606c62d4b3e9bfc227ccf983f4
Shared secret   4cf70a849193cabb08621501faf73538

http://www.last.fm/api/show/track.search

http://ws.audioscrobbler.com/2.0/?method=track.search&track=One More Time&artist=Daft Punk&api_key=1dda66606c62d4b3e9bfc227ccf983f4&format=json

http://ws.audioscrobbler.com/2.0/?method=track.search&track=Anchor Man&artist=Charli 2na&api_key=1dda66606c62d4b3e9bfc227ccf983f4&format=json&limit=1

http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=1dda66606c62d4b3e9bfc227ccf983f4&mbid=6b599a90-08ed-4217-a68e-969b76da7405&format=json



http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=1dda66606c62d4b3e9bfc227ccf983f4&mbid=3c9dbada-252b-4e12-93ab-4bc6527daf88&format=json


using musicbrainz
http://musicbrainz.org/ws/2/recording/?query=title:Raspberry%20Beret%20AND%20artist:Prince

OAuth Client ID         OAuth Client Secret
ct6dtH8LDWN3w7Gs6qJyUw  W6hRBIWvquICL_s2ELgGig

"""

import requests
from bs4 import BeautifulSoup
import re
import json
from urlparse import urljoin
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from bson.objectid import ObjectId
import datetime
import os

MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost/fmtrends')
print 'MONGODB_URI:',MONGODB_URI
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client.get_default_database()

BASE_URL = 'http://www.txfm.ie'
STATION  = 'TXFM'


def get_lastfm_info(track, artist):

    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        'method' : 'track.search',
        'track'  : track,
        'artist' : artist,
        'api_key': '1dda66606c62d4b3e9bfc227ccf983f4',
        'format' : 'json',
        'limit'  : 1
    }
    r = requests.get(url, params=params)
    result = r.json()['results']
    if int(result['opensearch:totalResults']) <= 0:
        # print artist
        # print track
        return None
    track = result['trackmatches']['track'][0]
    mbid = track['mbid'] or None
    url  = track['url'] or None
    lastfm_info = {
        'mbid': mbid,
        'url': url,
    }

    return lastfm_info


def alphanumeric(s):
    pattern = re.compile('[\W_]+')
    return pattern.sub('', s)

def get_key(artist, title):
    key = '{artist}-{song}'.format(
                artist = alphanumeric(artist).lower(), 
                song   = alphanumeric(title).lower()
            )
    return key

def get_tracks(soup, limit=None):
    """
        returns array of all songs with newest at index 0
    """

    thumbnails = soup.findAll('div', {'class','thumbnail'})
    thumbnails = thumbnails[1:]
    if limit:
        thumbnails = thumbnails[:limit]
    tracks = []

    for thumbnail in thumbnails:
        heading = thumbnail.text.strip().split(' - ', 1)
        artist  = heading[0]
        title   = heading[1]
        img     = thumbnail.find('img').attrs['src']
        key     = get_key(artist, title)
        track = {
            'artist': artist,
            'title' : title,
            'img'   : img,
            'key'   : key,
        }
        lastfm_info = get_lastfm_info(track['title'], track['artist'])
        if lastfm_info:
            track['mbid']        = lastfm_info['mbid']
            track['lastfm_url'] = lastfm_info['url']
        tracks.append(track)
    return tracks

def get_show(soup):
    header = soup.find('div', {'class','home_header'})
    show_link = header.find('h1').find('a')
    # title and url
    url   = show_link.attrs['href']
    title = show_link.text

    # time
    full_time   = header.find('p').text
    match = re.findall('(\d+\:\d+) - (\d+\:\d+)', full_time)
    start_time = None
    end_time   = None
    if len(match) > 0:
        start_time = match[0][0]
        end_time   = match[0][1]

    # description
    description = header.find('h3').text.strip()

    # get image
    img = soup.find('div', {'class','show_home'}).find('img').attrs['src']
    url = urljoin(BASE_URL, url)
    img = urljoin(BASE_URL, img)

    show = {
        "station"    : STATION,
        "title"      : title,
        "url"        : url, 
        "start_time" : start_time, 
        "end_time"   : end_time,
        "description": description,
        "image"      : img,
        "now_playing": True
    }
    return show

def get_soup():
    url = BASE_URL
    r = requests.get(url)
    html = r.text
    # print r.status_code
    if r.status_code != 200:
        return False
    return BeautifulSoup(html, "html.parser")

def add_show(show):
    """
        returns show+_id
    """
    # turn of now playing
    query = {
        'now_playing': True
    }
    update = {
        '$set':{
            'now_playing': False        
        }
    }
    db.shows.update(query, update)
    # Add/update show
    # Find by title
    query = {
        'title': show['title']
    }
    update = {
        '$set': show
    }
    r = db.shows.update(query, update, upsert=True)
    # print r
    return db.shows.find_one(query)

def upsert_tracks(tracks):
    tracks_updated = []

    bulk = db.tracks.initialize_unordered_bulk_op()


    for track in tracks:
        # insert/update track
        # search by 'key'
        query = {
            'key': track['key']
        }
        update = {
            '$set': track
        }
        r = bulk.find(query).upsert().update(update)
    try:
        # print 'trying insert'
        r=bulk.execute()
        # print r
    except BulkWriteError as bwe:
        print 'err:'
        print(bwe.details)
        return False

    # get _id's
    for track in tracks:
        # insert/update track
        # search by 'key'
        query = {
            'key': track['key']
        }
        track = db.tracks.find_one(query)
        tracks_updated.append(track)

    return tracks_updated

def add_plays(tracks, show):
    """
    {
        "track_id": ObjectId("1234"),
        "show_id": ObjectId("abcd"),
        "station": "TXFM"
        "played_at": "5/30/2016, 3:34:04 PM",
        "now_playing": true
    }
    """
    track_ids = [track['_id'] for track in tracks]
    # print track_ids
    # get all now_playing from this station
    query = {
        'now_playing': True,
        'station'    : STATION
    }
    now_playings = db.plays.find(query)
    for play in now_playings:
        # check if still play
        # set now_playing to false if not
        if play['track_id'] in track_ids:
            track_ids.remove(play['track_id'])
        else:
            # update to not playing
            query = {
                '_id': play['_id']
            }
            update = {
                '$set':{
                    'now_playing': False
                }
            }
            r = db.plays.update(query, update)

    # tracks not added as playing yet
    for track_id in track_ids:
        play = {
            'track_id'  : track_id,
            'show_id'   : show['_id'],
            'station'   : STATION,
            'played_at' : datetime.datetime.now(),
            'now_playing': True
        }
        # print play
        db.plays.insert(play)

def add_current_track(tracks):
    url = 'http://www.txfm.ie/assets/includes/ajax/player_info.php?type=On+Air&currentstationID=11'
    r = requests.get(url)
    response = r.json()
    artist   = response['currentArtist']
    title    = response['currentTitle']
    key      = get_key(artist, title)
    current_track = {
        'artist': artist,
        'title' : title,
        'img'   : '',
        'key'   : key,
    }
    lastfm_info = get_lastfm_info(current_track['title'], current_track['artist'])
    if lastfm_info:
        current_track['mbid']       = lastfm_info['mbid']
        current_track['lastfm_url'] = lastfm_info['url']

    track_keys = [track['key'] for track in tracks]
    if current_track['key'] not in track_keys:
        print '\n\tNot in!'
        print current_track
        tracks.append(current_track)
    return tracks

def cron():
    soup = get_soup()
    if not soup:
        return
    show = get_show(soup)
    # ensure show is added/get _id
    show = add_show(show)
    # print show
    tracks = get_tracks(soup)
    # add tracks/get their _ids
    tracks = add_current_track(tracks)
    tracks = upsert_tracks(tracks)
    # print tracks
    add_plays(tracks, show)

def main():
    cron()
    # print json.dumps(get_mbid('Gin Soaked Boy', 'The Divine Comedy'), indent=2)

if __name__ == '__main__':
    main()
