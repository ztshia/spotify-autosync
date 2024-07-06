import requests
import base64
import json
from opencc import OpenCC
from datetime import datetime, timezone
import os

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('SPOTIFY_REFRESH_TOKEN')

def get_access_token():
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN
    }
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    return response.json()['access_token']

def fetch_liked_songs(access_token):
    url = 'https://api.spotify.com/v1/me/tracks?limit=50'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    songs = []
    while url:
        response = requests.get(url, headers=headers)
        data = response.json()
        songs.extend(data['items'])
        url = data.get('next')
    return songs

access_token = get_access_token()
songs = fetch_liked_songs(access_token)

simplified_songs = []
cc = OpenCC('t2s')
for item in songs:
    track = item['track']
    song_info = {
        'song_name': cc.convert(track['name']),
        'singer_name': cc.convert(', '.join([artist['name'] for artist in track['artists']])),
        'added_at': item['added_at']
    }
    simplified_songs.append(song_info)

with open('liked_songs.json', 'w', encoding='utf-8') as f:
    json.dump(simplified_songs, f, ensure_ascii=False, indent=4)
