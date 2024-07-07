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

def download_album_cover(album_cover_url, album_cover_path):
    response = requests.get(album_cover_url)
    if response.status_code == 200:
        with open(album_cover_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded album cover to {album_cover_path}")
    else:
        print(f"Failed to download album cover from {album_cover_url}")

def save_to_json(data, filename='top_tracks.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"File {filename} saved successfully.")

def create_simple_top_tracks(data, filename='simple_top_tracks.json'):
    simple_tracks = []
    cc = OpenCC('t2s')  # 创建简繁转换器，从繁体字转换为简体字
    
    for track in data['items']:
        simple_track = {
            'song_name': cc.convert(track['name']),
            'singer_name': cc.convert(track['artists'][0]['name']),
            'added_at': track['added_at'],
            'album_name': cc.convert(track['album']['name']),
            'album_cover_url': track['album']['images'][0]['url'],
            'album_cover_path': f"top/{track['album']['id']}.jpg",  # 保存到 top 文件夹下，使用专辑 ID 命名文件
            'track_duration_ms': track['duration_ms'],
            'popularity': track['popularity'],
            'track_url': track['external_urls']['spotify']
        }
        simple_tracks.append(simple_track)
        download_album_cover(simple_track['album_cover_url'], simple_track['album_cover_path'])

    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(simple_tracks, file, indent=4, ensure_ascii=False)
    print(f"File {filename} saved successfully.")

if __name__ == '__main__':
    try:
        access_token = get_access_token()
        top_tracks = get_top_tracks(access_token)
        save_to_json(top_tracks)

        # 生成简化版的 JSON 文件
        create_simple_top_tracks(top_tracks)
        print('最常听的歌曲已保存到 top_tracks.json 和 simple_top_tracks.json 文件中')
    except Exception as e:
        print(f"Error: {e}")
