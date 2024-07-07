import requests
import json
import base64
import os
from datetime import datetime
from opencc import OpenCC

# OpenCC converter for Traditional Chinese to Simplified Chinese
cc = OpenCC('t2s')

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
REFRESH_TOKEN = os.getenv('SPOTIFY_REFRESH_TOKEN')

def get_access_token():
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {base64.b64encode((CLIENT_ID + ":" + CLIENT_SECRET).encode()).decode()}',
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN,
    }
    response = requests.post(token_url, headers=headers, data=data)
    
    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.status_code}, {response.text}")

    response_data = response.json()
    if 'access_token' not in response_data:
        raise Exception(f"Access token not found in response: {response_data}")

    return response_data['access_token']

def get_top_tracks(access_token):
    top_tracks_url = 'https://api.spotify.com/v1/me/top/tracks'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = {
        'limit': 50,  # 可根据需要调整获取的数量
        'time_range': 'short_term'  # 可根据需要调整时间范围：short_term, medium_term, long_term
    }
    response = requests.get(top_tracks_url, headers=headers, params=params)
    return response.json()

def download_album_cover(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded album cover to {path}")
    else:
        print(f"Failed to download album cover from {url}")

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"File {filename} saved successfully.")

def save_top_tracks(data, filename='top_tracks.json'):
    top_tracks = []
    for item in data['items']:
        track = item

        album_cover_url = track['album']['images'][0]['url'] if track['album']['images'] else ''
        album_cover_path = f"top/{track['id']}.jpg" if album_cover_url else ''

        top_tracks.append({
          'song_name': cc.convert(track['name']),
            'singer_name': cc.convert(', '.join(artist['name'] for artist in track['artists'])),
            'added_at': item['added_at'],
            'album_name': cc.convert(track['album']['name']),
            'album_cover_url': album_cover_url,
            'album_cover_path': album_cover_path,
            'track_duration_ms': track['duration_ms'],
            'popularity': track['popularity'],
            'track_url': track['external_urls']['spotify']
        })

        if album_cover_url:
            download_album_cover(album_cover_url, album_cover_path)

    save_to_json(top_tracks, filename)

def save_simple_top_tracks(data, filename='simple_top_tracks.json'):
    simple_top_tracks = []
    for item in data['items']:
        track = item

        simple_top_tracks.append({
            'song_name': cc.convert(track['name']),
            'singer_name': cc.convert(', '.join(artist['name'] for artist in track['artists'])),
            'added_at': track['added_at']
        })

    save_to_json(simple_top_tracks, filename)

if __name__ == '__main__':
    try:
        os.makedirs('top', exist_ok=True)
        access_token = get_access_token()
        top_tracks_data = get_top_tracks(access_token)
        save_top_tracks(top_tracks_data)
        save_simple_top_tracks(top_tracks_data)
        print(f'已将最常听的歌曲保存到 top_tracks.json 和 simple_top_tracks.json 文件中')
    except Exception as e:
        print(f"Error: {e}")
