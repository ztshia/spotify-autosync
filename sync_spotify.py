import requests
import json
import base64
import os

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

def save_to_json(data, filename='liked_tracks.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    try:
        access_token = get_access_token()
        liked_tracks = get_liked_tracks(access_token)
        save_to_json(liked_tracks)
        print(f'已将点赞的歌曲保存到liked_tracks.json文件中')
    except Exception as e:
        print(f"Error: {e}")
