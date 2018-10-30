import requests
import json
import feedparser
import anitopy
from yaml import load, dump

rpcUrl = 'http://localhost:9091/transmission/rpc'

def check_anime(title, feed):
    info = anitopy.parse(title)
    for anime in feed['anime-list']:
        if anime == info['anime_title']:
            if info['video_resolution'] == feed['resolution']:
                return True
            return False
    
    return False

def get_session_id():
    res = requests.get(rpcUrl)
    return res.headers['X-Transmission-Session-Id']

def add_torrent(torrent):
    sessionId = get_session_id()
    
    headers = {
        'content-type': 'application/json',
        'X-Transmission-Session-Id': sessionId
    }
    
    payload = {
        'method': 'torrent-add',
        'arguments': {
            'filename': torrent
        }
    }

    response = requests.post(
        rpcUrl, data=json.dumps(payload), headers=headers).json()

    print(response)

def handle_feed(feed):
    result = feedparser.parse(feed['url'])
    
    for entry in result.entries:
        if check_anime(entry.title, feed):
            add_torrent(entry.guid)

def main():
    data = None
    with open('config.yml', 'r') as file:
        data = load(file)
    
    for feed in data['feeds']:
        handle_feed(feed)

if __name__ == '__main__':
    main()
