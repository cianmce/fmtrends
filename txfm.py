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
from bson.objectid import ObjectId



MONGODB_URI  = 'mongodb://localhost/fmtrends'
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client.get_default_database()

BASE_URL = 'http://www.txfm.ie'


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

def get_tracks(soup):
    """
        returns array of all songs with newest at index 0
    """

    thumbnails = soup.findAll('div', {'class','thumbnail'})
    thumbnails = thumbnails[1:]
    tracks = []

    for thumbnail in thumbnails:
        heading = thumbnail.text.strip().split(' - ', 1)
        artist  = heading[0]
        title   = heading[1]
        img     = thumbnail.find('img').attrs['src']
        key     = '{artist}-{song}'.format(
                artist = alphanumeric(artist).lower(), 
                song   = alphanumeric(title).lower()
            )
        track = {
            'artist': artist,
            'title' : title,
            'img'   : img,
            'key'   : key,
            "now_playing": True
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
        "title"      : title,
        "url"        : url, 
        "start_time" : start_time, 
        "end_time"   : end_time,
        "description": description,
        "image"      : img,
        "now_playing": True
    }
    return show

def cron():
    url = BASE_URL
    r = requests.get(url)
    html = r.text
    print r.status_code
    if r.status_code != 200:
        return False
    soup   = BeautifulSoup(html, "html.parser")
    show   = get_show(soup)
    print show
    tracks = get_tracks(soup)
    print json.dumps(tracks)

    # 


def main():
    cron()
    # print json.dumps(get_mbid('Gin Soaked Boy', 'The Divine Comedy'), indent=2)

if __name__ == '__main__':
    main()
