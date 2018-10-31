import requests
import json
import feedparser
import anitopy
from yaml import load, dump


config = {
    'resolution': None,
    'rpc-url': None
}

feeds = []

def check_torrent(title, feed_id):
    info = anitopy.parse(title)

    check_title = False
    check_resolution = False

    if len(feeds[feed_id]['resolutions']) == 0:
        feeds[feed_id]['resolutions'] = [config['resolution']]

    try:
        if info['video_resolution'] in feeds[feed_id]['resolutions']:
            check_resolution = True
    except KeyError:
        check_resolution = False

    if len(feeds[feed_id]['anime-list']) == 0:
        check_title = True
    else:
        for anime in feeds[feed_id]['anime-list']:
            if anime['title'] == info['anime_title']:
                check_title = True
                try:
                    if anime['resolution'] == info['video_resolution']:
                        check_resolution = True
                    else:
                        check_resolution = False
                except KeyError:
                    print('No resolution was set for the anime: %s' % anime['title'])

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

def handle_feeds():
    for index, feed in enumerate(feeds):
        if not feed['enabled']:
            continue
        
        torrent = feedparser.parse(feed['url'])
        for entry in torrent.entries:
            if check_torrent(entry.title, int(index)):
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

    # Load feeds
    for feed in data['feeds']:
        feeds.append(feed)

    return data

def main():
    data = load_config('config.yml')
    print(data['rpc-server'])
    
    handle_feeds()

if __name__ == '__main__':
    main()
