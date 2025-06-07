import json
from openai import OpenAI

client = OpenAI(base_url="https://api.deepseek.com/v1", api_key="sk-d7aaf190677c4155980e44e79eb9739a")

# 加载你的 Spotify 数据
with open("liked_tracks.json", "r", encoding="utf-8") as f:
    liked_tracks = json.load(f)

# 构造提示词（可根据需要优化）
prompt = f"""
请根据以下 Spotify 听歌记录分析用户的音乐品味：
{json.dumps(liked_tracks, ensure_ascii=False, indent=2)}

输出一份 taste.json，格式为：
{{
  "summary": "你的总体品味概述，约500字的一段话",
  "genres": ["流派A", "流派B"],
  "moods": ["情绪A", "情绪B"],
  "description": "更详细的描述，可能的用户画像，不少于2000字的几段话"
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
