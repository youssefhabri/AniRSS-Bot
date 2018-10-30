import requests
import json
import feedparser
import anitopy
from yaml import load, dump


config = {
    'resolution': None,
    'rpc-url': None
}

def check_anime(title, feed):
    info = anitopy.parse(title)

    if len(feed['resolutions']) == 0:
        feed['resolutions'] = [config['resolution']]

    check_title = False
    check_resolution = False

    if len(feed['anime-list']) == 0:
        check_title = True
    else:
        for anime in feed['anime-list']:
            if anime == info['anime_title']:
                check_title = True
                continue
            check_title = False
    try:
        if info['video_resolution'] in feed['resolutions']:
            check_resolution = True
    except:
        check_resolution = False

    return check_title and check_resolution

def get_session_id():
    res = requests.get(config['rpc-url'])
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
        config['rpc-url'], data=json.dumps(payload), headers=headers).json()

    print(response)

def handle_feed(feed):
    result = feedparser.parse(feed['url'])
    
    for entry in result.entries:
        if check_anime(entry.title, feed):
            add_torrent(entry.guid)

def load_config(filename):
    data = None
    with open(filename, 'r') as file:
        data = load(file)
    
    # Set default resolution
    try:
        config['resolution'] = data['default-resolution']
    except KeyError:
        config['resolution'] = '720p'

    # Set RPC URL
    try:
        config['rpc-url'] = data['rpc-server']['protocol'] + '://' + data['rpc-server']['host'] + ':' + data['rpc-server']['post'] + data['rpc-server']['path']
    except KeyError:
        config['rpc-url'] = 'http://localhost:9091/transmission/rpc'

    return data

def main():
    data = load_config('config.yml')
    print(data['rpc-server'])
    pass
    for feed in data['feeds']:
        if feed['enabled']:
            handle_feed(feed)

if __name__ == '__main__':
    main()
