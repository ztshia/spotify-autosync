import requests
import json
import base64
import os
from opencc import OpenCC

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
REFRESH_TOKEN = os.getenv('SPOTIFY_REFRESH_TOKEN')

# 使用默认配置初始化 OpenCC
cc = OpenCC('t2s')

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

def download_image(url, folder='top'):
    response = requests.get(url)
    if response.status_code == 200:
        parsed_url = urlparse(url)
        image_name = os.path.basename(parsed_url.path)
        Path(folder).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(folder, image_name), 'wb') as file:
            file.write(response.content)
        return os.path.join(folder, image_name)
    else:
        raise Exception(f"Failed to download image: {response.status_code}, {response.text}")

def transform_data(track):
    album_cover_url = track['album']['images'][0]['url']
    album_cover_path = download_image(album_cover_url, folder='top')
    return {
        "song_name": cc.convert(track['name']),
        "singer_name": cc.convert(', '.join(artist['name'] for artist in track['artists'])),
        "added_at": track['added_at'],
        "album_name": cc.convert(track['album']['name']),
        "album_cover_url": album_cover_url,
        "album_cover_path": album_cover_path,
        "track_duration_ms": track['duration_ms'],
        "popularity": track['popularity'],
        "track_url": track['external_urls']['spotify']
    }

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"File {filename} saved successfully.")

if __name__ == '__main__':
    try:
        access_token = get_access_token()
        top_tracks = get_top_tracks(access_token)['items']
        
        detailed_tracks = [transform_data(track) for track in top_tracks]
        simple_tracks = [{
            "song_name": cc.convert(track['name']),
            "singer_name": cc.convert(', '.join(artist['name'] for artist in track['artists'])),
            "added_at": track['added_at']
        } for track in top_tracks]
        
        save_to_json(detailed_tracks, 'top_tracks.json')
        save_to_json(simple_tracks, 'simple_top_tracks.json')
        
        print('最常听的歌曲已保存到 top_tracks.json 和 simple_top_tracks.json 文件中')
    except Exception as e:
        print(f"Error: {e}")
