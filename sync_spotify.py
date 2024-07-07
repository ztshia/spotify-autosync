import requests
import json
import base64
import os
from opencc import OpenCC

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

def get_liked_tracks(access_token):
    tracks_url = 'https://api.spotify.com/v1/me/tracks'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = {
        'limit': 50
    }
    response = requests.get(tracks_url, headers=headers, params=params)
    return response.json()

def save_to_json(data, filename='simple_liked_tracks.json'):
    simple_data = []
    for item in data['items']:
        track = item['track']
        simple_data.append({
            'song_name': track['name'],
            'singer_name': ', '.join(artist['name'] for artist in track['artists']),
            'added_at': item['added_at']
        })

    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(simple_data, file, indent=4, ensure_ascii=False)
    print(f"File {filename} saved successfully.")

def convert_to_simplified_chinese(filename):
    cc = OpenCC('t2s')  # 繁体中文转简体中文
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    converted_data = []
    for item in data:
        converted_item = {
            'song_name': cc.convert(item['song_name']),
            'singer_name': cc.convert(item['singer_name']),
            'added_at': item['added_at']
        }
        converted_data.append(converted_item)
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(converted_data, file, indent=4, ensure_ascii=False)
    print(f"File {filename} converted to simplified Chinese successfully.")

if __name__ == '__main__':
    try:
        access_token = get_access_token()
        liked_tracks = get_liked_tracks(access_token)
        save_to_json(liked_tracks)
        convert_to_simplified_chinese('simple_liked_tracks.json')
        print(f'已将点赞的歌曲保存到 simple_liked_tracks.json 并转换为简体中文')
    except Exception as e:
        print(f"Error: {e}")
