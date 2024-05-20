import requests
import subprocess
import tempfile
import os
import json

def get_baidu_token(api_key, secret_key):
    """获取百度API的访问令牌。"""
    auth_url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        'grant_type': 'client_credentials',
        'client_id': api_key,
        'client_secret': secret_key
    }
    response = requests.get(auth_url, params=params)
    response_json = response.json()
    return response_json['access_token']

def text_to_speech(text,token):
    url = "https://tsn.baidu.com/text2audio"
    
    # 对文本进行URL编码
    text_encoded = requests.utils.quote(text)
    
    payload = f'tex={text_encoded}&tok={token}&cuid=HyNryfzaVoRspq8fHRXaTcWPiQvDkwL6&ctp=1&lan=zh&spd=5&pit=5&vol=5&per=1&aue=6'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*'
    }
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        # 如果请求成功，返回音频二进制数据
        return response.content
    else:
        # 输出错误信息
        print("Error:", response.status_code, response.text)
        return None

def play_audio(audio_data):
    """播放音频数据。"""
    with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as f:
        f.write(audio_data)
        f.flush()
        subprocess.run(['aplay', f.name])

def main():

    # 获取当前脚本文件所在的绝对路径
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # 获取上一级目录
    parent_dir_path = os.path.dirname(dir_path)

    # 在上一级目录中构建 config.json 的路径
    config_path = os.path.join(parent_dir_path, 'config.json')
    
    with open(config_path, 'r') as file:
        config = json.load(file)

    text = '你好，这是一个测试。'

    token = get_baidu_token(config['baidu_api_key'], config['baidu_secret_key'])
    audio_data = text_to_speech(text, token)

    if audio_data:
        play_audio(audio_data)
    else:
        print("Failed to synthesize speech.")

if __name__ == '__main__':
    main()
