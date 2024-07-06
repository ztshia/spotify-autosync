import requests
import base64
import json
from opencc import OpenCC
import os

def get_access_token(client_id, client_secret):
    auth_str = f'{client_id}:{client_secret}'
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {b64_auth_str}',
    }
    data = {
        'grant_type': 'client_credentials'
    }

    response = requests.post(token_url, headers=headers, data=data)
    response_data = response.json()
    return response_data['access_token']

def fetch_playlist(playlist_id, access_token):
    songs_list = []
    next_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=100'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    while next_url:
        response = requests.get(next_url, headers=headers)
        data = response.json()
        songs_list.extend(data['items'])
        next_url = data['next']

    return songs_list

def convert_to_simplified_chinese(text):
    cc = OpenCC('t2s')
    return cc.convert(text)

def download_image(url, path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

def main():
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    playlist_id = '44k9yc7Q1M2otYb6pdfxfg'
    album_dir = 'album'

    if not os.path.exists(album_dir):
        os.makedirs(album_dir)

    access_token = get_access_token(client_id, client_secret)
    playlist_data = fetch_playlist(playlist_id, access_token)

    songs_list = []
    full_songs_list = []

    for item in playlist_data:
        track = item['track']
        added_at = item['added_at']
        song_name = convert_to_simplified_chinese(track['name'])
        singer_name = convert_to_simplified_chinese(', '.join([artist['name'] for artist in track['artists']]))
        album = track['album']
        album_name = convert_to_simplified_chinese(album['name'])
        album_cover_url = album['images'][0]['url'] if album['images'] else ''
        album_cover_path = os.path.join(album_dir, f"{album['id']}.jpg")

        # Download album cover if it doesn't already exist
        if album_cover_url and not os.path.exists(album_cover_path):
            download_image(album_cover_url, album_cover_path)

        # 构造简化歌曲信息
        song_info = {
            'song_name': song_name,
            'singer_name': singer_name,
            'added_at': added_at
        }
        songs_list.append(song_info)

        # 构造完整歌曲信息
        full_song_info = {
            'song_name': song_name,
            'singer_name': singer_name,
            'added_at': added_at,
            'album_name': album_name,
            'album_cover_url': album_cover_url,
            'album_cover_path': album_cover_path,
            'track_duration_ms': track['duration_ms'],
            'popularity': track['popularity'],
            'track_url': track['external_urls']['spotify']
        }
        full_songs_list.append(full_song_info)

    # 生成简化 JSON 文件
    songs_json = json.dumps(songs_list, ensure_ascii=False, indent=4)
    with open('playlist.json', 'w', encoding='utf-8') as file:
        file.write(songs_json)

    # 生成完整 JSON 文件
    full_songs_json = json.dumps(full_songs_list, ensure_ascii=False, indent=4)
    with open('full_playlist.json', 'w', encoding='utf-8') as file:
        file.write(full_songs_json)

if __name__ == '__main__':
    main()
