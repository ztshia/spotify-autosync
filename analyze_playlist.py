import os
import json
import requests

def analyze_playlist():
    # 读取 liked_tracks.json
    with open('liked_tracks.json', 'r', encoding='utf-8') as f:
        liked_tracks = json.load(f)

    # 构建提示词
    prompt = f"""
你是一个音乐品位分析专家，请根据以下 Spotify 听歌记录分析用户的音乐品位和画像，输出一个 JSON 格式的摘要：
- 统计主要喜欢的歌手、语言、年代、流派
- 给出整体听歌偏好（如「偏爱粤语女声」或「流行金曲爱好者」）
- 给出代表性的歌曲推荐（可从本记录中挑选）
- 输出风格：简洁中文，结构化 JSON 格式
输入数据如下：
{json.dumps(liked_tracks, ensure_ascii=False)}
"""

    # 调用 DeepSeek API
    api_key = os.getenv('DEEPSEEK_API_KEY')
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    response = requests.post('https://api.deepseek.com/v1/chat/completions', headers=headers, json=data)
    result = response.json()
    taste_json = result['choices'][0]['message']['content']

    # 保存为 taste.json
    with open('taste.json', 'w', encoding='utf-8') as f:
        f.write(taste_json)

if __name__ == "__main__":
    analyze_playlist()



import json
from openai import OpenAI

client = OpenAI(base_url="https://api.deepseek.com/v1", api_key="DEEPSEEK_API_KEY")

# 加载你的 Spotify 数据
with open("liked_tracks.json", "r", encoding="utf-8") as f:
    liked_tracks = json.load(f)

# 构造提示词（可根据需要优化）
prompt = f"""
请根据以下 Spotify 听歌记录分析用户的音乐品味：
{json.dumps(liked_tracks, ensure_ascii=False, indent=2)}

输出一份 taste.json，格式为：
{{
  "summary": "你的总体品味概述",
  "genres": ["流派A", "流派B"],
  "moods": ["情绪A", "情绪B"],
  "description": "更详细的描述"
}}
"""

# 调用 DeepSeek
completion = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
)

# 提取 JSON 结构
import re

match = re.search(r"\{.*\}", completion.choices[0].message.content, re.DOTALL)
if match:
    result_json = json.loads(match.group())
    with open("taste.json", "w", encoding="utf-8") as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)
    print("taste.json 已生成。")
else:
    print("未能提取 JSON 输出，请检查提示词或模型返回内容。")
