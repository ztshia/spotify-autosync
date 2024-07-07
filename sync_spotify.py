import requests
import json
import base64
import os
import urllib.parse
import urllib.request
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

def download_album_cover(url, filename):
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"Downloaded album cover from {url} to {filename}")
    except Exception as e:
        print(f"Error downloading album cover: {e}")

def save_to_json_full(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"Full data saved to {filename} successfully.")

def save_to_json_simple(data, filename):
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
    print(f"Simple data saved to {filename} successfully.")

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

        # 保存完整版 liked_tracks.json
        save_to_json_full(liked_tracks, 'liked_tracks.json')

        # 保存简化版 simple_liked_tracks.json
        save_to_json_simple(liked_tracks, 'simple_liked_tracks.json')

        # 下载封面并保存到指定路径
        for item in liked_tracks['items']:
            track = item['track']
            album_cover_url = track['album']['images'][0]['url']  # 获取封面图片URL
            album_cover_filename = f"favorited/album/{track['album']['id']}.jpg"  # 指定保存路径和文件名
            download_album_cover(album_cover_url, album_cover_filename)

        # 将 simple_liked_tracks.json 转换为简体中文
        convert_to_simplified_chinese('simple_liked_tracks.json')

        print(f'已将点赞的歌曲保存到 liked_tracks.json 并转换为简体中文')
    except Exception as e:
        print(f"Error: {e}")
