### 功能简介

自动同步Spotify已点赞的歌曲和指定歌单，生成json文件。

### 使用步骤

1.Fork本项目，删除根目录的所有Json文件。

2.注册[Spotify开发者](https://developer.spotify.com/dashboard/)账号并创建一个应用。访问Spotify开发者网站。
  登录后，创建一个新应用，获取客户端ID（**Client ID**）和客户端密钥（**Client Secret**）。
  
3.访问 https://accounts.spotify.com/authorize?client_id=your_client_id&response_type=code&redirect_uri=your_redirect_uri&scope=user-library-read (将加粗部分更换为你刚才获取的Client ID与填写的redirect_uri)，获取到**auth code**。

4.本地运行以下脚本，获得Refresh Token

```
import requests
import base64

CLIENT_ID = '**your_client_id**'
CLIENT_SECRET = '**your_client_secret**'
REDIRECT_URI = '**your_redirect_uri**'
AUTH_CODE = '**your_authorization_code**'  # 替换为你获取的授权码

def get_tokens(auth_code):
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {base64.b64encode((CLIENT_ID + ":" + CLIENT_SECRET).encode()).decode()}',
    }
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
    }
    response = requests.post(token_url, headers=headers, data=data)
    return response.json()

tokens = get_tokens(AUTH_CODE)
print(tokens)  # 这将包含 access_token 和 refresh_token

```

5.从脚本返回的数据中得到refresh_token，并填写到GitHub Secrets中：

- 进入你的GitHub仓库。
- 导航到 "Settings" -> "Secrets and variables" -> "Actions"。
- 点击 "New repository secret"，然后添加以下Secrets：
  - SPOTIFY_CLIENT_ID
  - SPOTIFY_CLIENT_SECRET
  - SPOTIFY_REDIRECT_URI
  - SPOTIFY_REFRESH_TOKEN（从上面的代码中获取）
 
6.完成

---


### Function Introduction
Automatically sync Spotify likes songs with the specified song list to generate a json file.

### Steps

1. Fork this project and delete all Json files in the root directory.

2. Sign up for a Spotify developer account and create an app. Visit the Spotify developer website. After logging in, create a new application and obtain the client ID and client secret.
   
3. Visit https://accounts.spotify.com/authorize? client_id=your_client_id&response_type=code&redirect_uri=your_redirect_uri&scope=user-library-read (Replace the bolded part with the Client ID you just obtained and the redirect_uri you filled in) to get the auth code.

4. Run the following script locally to obtain the Refresh Token

```
import requests
import base64
CLIENT_ID = '**your_client_id**'
CLIENT_SECRET = '**your_client_secret**'
REDIRECT_URI = '**your_redirect_uri**'
AUTH_CODE = '**your_authorization_code**' #Replace with the authorization code you obtained

def get_tokens(auth_code):
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {base64.b64encode((CLIENT_ID + ":" + CLIENT_SECRET).encode()).decode()}',
    }
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
    }
    response = requests.post(token_url, headers=headers, data=data)
    return response.json()

tokens = get_tokens(AUTH_CODE)
print(tokens) #This will include access_token and refresh_token

```

5. Get refresh_token from the data returned by the script and fill it in GitHub Secrets:
- Go to your GitHub repository.
- Navigate to "Settings" -> "Secrets and variables" -> "Actions".
- Click "New repository secret" and add the following Secrets:
  - SPOTIFY_CLIENT_ID
  - SPOTIFY_CLIENT_SECRET
  - SPOTIFY_REDIRECT_URI
  - SPOTIFY_REFRESH_TOKEN (obtained from the code above)

6. Completed
