import requests
import json
import os

# API URL
url = 'https://wishub-x1.ctyun.cn/v1/chat/completions'

# 替换成你的 API Key
api_key = "44d330c0fe7e4baaa3efbb5a0f8491e2"

# 请求头
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'  # 替换为您的 API Key
}

# 请求数据
data = {
    "messages": [
        {
            "role": "system",
            "content": "You are a test assistant."
        },
        {
            "role": "user",
            "content": "Testing. Just say hi and nothing else."
        }
    ],
    "model": "7ba7726dad4c4ea4ab7f39c7741aea68"  # DeepSeek-R1模型名
}

# 发送 POST 请求
response = requests.post(url, headers=headers, json=data)

# 输出响应内容
print(response)
print("="*20)
print(response.json())
