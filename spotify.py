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
    playlist_url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(playlist_url, headers=headers)
    return response.json()

def convert_to_simplified_chinese(text):
    cc = OpenCC('t2s')
    return cc.convert(text)

def main():
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    playlist_id = '44k9yc7Q1M2otYb6pdfxfg'

    access_token = get_access_token(client_id, client_secret)
    playlist_data = fetch_playlist(playlist_id, access_token)

    songs_list = []
    for item in playlist_data['tracks']['items']:
        track = item['track']
        added_at = item['added_at']
        song_name = convert_to_simplified_chinese(track['name'])
        singer_name = convert_to_simplified_chinese(', '.join([artist['name'] for artist in track['artists']]))
        song_info = {
            'song_name': song_name,
            'singer_name': singer_name,
            'added_at': added_at
        }
        songs_list.append(song_info)

    songs_json = json.dumps(songs_list, ensure_ascii=False, indent=4)
    with open('playlist.json', 'w', encoding='utf-8') as file:
        file.write(songs_json)

if __name__ == '__main__':
    main()
