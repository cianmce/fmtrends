import requests
from bs4 import BeautifulSoup
import re
import json


"""
API key 1dda66606c62d4b3e9bfc227ccf983f4
Shared secret   4cf70a849193cabb08621501faf73538

http://www.last.fm/api/show/track.search

http://ws.audioscrobbler.com/2.0/?method=track.search&track=One More Time&artist=Daft Punk&api_key=1dda66606c62d4b3e9bfc227ccf983f4&format=json

http://ws.audioscrobbler.com/2.0/?method=track.search&track=Anchor Man&artist=Charli 2na&api_key=1dda66606c62d4b3e9bfc227ccf983f4&format=json&limit=1

http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=1dda66606c62d4b3e9bfc227ccf983f4&mbid=6b599a90-08ed-4217-a68e-969b76da7405&format=json



http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=1dda66606c62d4b3e9bfc227ccf983f4&mbid=3c9dbada-252b-4e12-93ab-4bc6527daf88&format=json



"""

def get_mbid(track, artist):

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
    if result['opensearch:totalResults'] <= 0:
        return None
    track = result['trackmatches']['track'][0]
    print json.dumps(track)
    return track['mbid']


def alphanumeric(s):
    pattern = re.compile('[\W_]+')
    return pattern.sub('', s)

def get_tracks():
    url = 'http://www.txfm.ie'
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    # print dir(soup)
    thumbnails = soup.findAll('div', {'class','thumbnail'})

    thumbnail = thumbnails[1]

    heading = thumbnail.text.strip().split(' - ', 1)
    artist  = heading[0]
    track   = heading[1]
    img     = thumbnail.find('img').attrs['src']

    key        = '{artist}-{song}'.format(
                        artist = alphanumeric(artist).lower(), 
                        song   = alphanumeric(track).lower()
                    )

    song = {
        'artist': artist,
        'title' : track,
        'img'   : img,
        'key'   : key,
        'mbid'  : get_mbid(track, artist)
    }
    print json.dumps(song, indent=2)



def main():
    get_tracks()
    # print json.dumps(get_mbid('Gin Soaked Boy', 'The Divine Comedy'), indent=2)

if __name__ == '__main__':
    main()
