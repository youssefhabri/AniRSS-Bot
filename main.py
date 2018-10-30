import requests
import json
import feedparser
import anitopy

userList = ['Black Clover', 'Golden Kamuy']

feedUrl = 'http://www.shanaproject.com/feeds/subber/Erai-raws/'
rpcUrl = 'http://localhost:9091/transmission/rpc'

def check_anime(title, resolution):
    info = anitopy.parse(title)
    for anime in userList:
        if anime == info['anime_title']:
            if info['video_resolution'] == resolution:
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

def main():
    feed = feedparser.parse(feedUrl)
    
    for entry in feed.entries:
        if check_anime(entry.title, '720p'):
            add_torrent(entry.guid)

if __name__ == '__main__':
    main()
