import requests
import json
import base64
import os
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
    tracks_url = 'https://api.spotify.com/v1/me/top/tracks'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = {
        'time_range': 'long_term',  # Change time_range if needed
        'limit': 50
    }
    response = requests.get(tracks_url, headers=headers, params=params)
    return response.json()

def download_album_cover(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded album cover to {path}")
    else:
        print(f"Failed to download album cover from {url}")

def save_to_json(data, filename='top_tracks.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"File {filename} saved successfully.")

def save_simple_top_tracks(data, filename='simple_top_tracks.json'):
    simple_tracks = []
    for item in data['items']:
        track = item

        simple_tracks.append({
            'song_name': cc.convert(track['name']),
            'singer_name': cc.convert(', '.join(artist['name'] for artist in track['artists'])),
            'added_at': track['album']['release_date'],  # Adjust as needed
            'album_name': cc.convert(track['album']['name']),
            'album_cover_url': track['album']['images'][0]['url'] if track['album']['images'] else '',
            'album_cover_path': f"top/{track['id']}.jpg" if track['album']['images'] else '',
            'track_duration_ms': track['duration_ms'],
            'popularity': track['popularity'],
            'track_url': track['external_urls']['spotify']
        })

        if track['album']['images']:
            download_album_cover(track['album']['images'][0]['url'], f"top/{track['id']}.jpg")

    save_to_json(simple_tracks, filename)

if __name__ == '__main__':
    try:
        os.makedirs('top', exist_ok=True)
        access_token = get_access_token()
        top_tracks_data = get_top_tracks(access_token)
        save_to_json(top_tracks_data, 'top_tracks.json')
        save_simple_top_tracks(top_tracks_data, 'simple_top_tracks.json')
        print(f'已将最常听的歌曲保存到 top_tracks.json 和 simple_top_tracks.json 文件中')
    except Exception as e:
        print(f"Error: {e}")
