import requests
import json
import base64
import os
from opencc import OpenCC

# Initialize OpenCC for converting to Simplified Chinese
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

def download_album_cover(url, path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(path, 'wb') as file:
            for chunk in response:
                file.write(chunk)
        print(f"Downloaded album cover to {path}")
    else:
        print(f"Failed to download album cover from {url}")

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"File {filename} saved successfully.")

if __name__ == '__main__':
    try:
        access_token = get_access_token()
        top_tracks_data = get_top_tracks(access_token)
        top_tracks = []
        simple_top_tracks = []

        for item in top_tracks_data['items']:
            track_info = {
                "song_name": cc.convert(item['name']),
                "singer_name": cc.convert(item['artists'][0]['name']),
                "added_at": item['added_at'],
                "album_name": cc.convert(item['album']['name']),
                "album_cover_url": item['album']['images'][0]['url'],
                "album_cover_path": f"top/{item['id']}.jpg",
                "track_duration_ms": item['duration_ms'],
                "popularity": item['popularity'],
                "track_url": item['external_urls']['spotify']
            }
            top_tracks.append(track_info)

            simple_track_info = {
                "song_name": cc.convert(item['name']),
                "singer_name": cc.convert(item['artists'][0]['name']),
                "added_at": item['added_at']
            }
            simple_top_tracks.append(simple_track_info)

            # Download album cover
            download_album_cover(item['album']['images'][0]['url'], track_info['album_cover_path'])

        save_to_json(top_tracks, 'top_tracks.json')
        save_to_json(simple_top_tracks, 'simple_top_tracks.json')

        print('最常听的歌曲已保存到 top_tracks.json 和 simple_top_tracks.json 文件中')
    except Exception as e:
        print(f"Error: {e}")
