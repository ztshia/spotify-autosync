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

    return response.json()['access_token']

def get_top_tracks(access_token, time_range='medium_term'):
    url = 'https://api.spotify.com/v1/me/top/tracks'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = {
        'time_range': time_range,  # 可选值：'short_term', 'medium_term', 'long_term'
        'limit': 50  # 最大值为50
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Failed to get top tracks: {response.status_code}, {response.text}")

    return response.json()

def save_to_json(data, filename='top_tracks.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"File {filename} saved successfully.")

if __name__ == '__main__':
    try:
        access_token = get_access_token()
        top_tracks = get_top_tracks(access_token)
        save_to_json(top_tracks)
        print('最常听的歌曲已保存到 top_tracks.json 文件中')
    except Exception as e:
        print(f"Error: {e}")
