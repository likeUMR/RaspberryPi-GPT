import requests
import subprocess
import tempfile
import queue
import threading
from urllib.parse import quote

def get_baidu_token(api_key, secret_key):
    auth_url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        'grant_type': 'client_credentials',
        'client_id': api_key,
        'client_secret': secret_key
    }
    response = requests.get(auth_url, params=params)
    response_json = response.json()
    return response_json['access_token']

def text_to_speech(text, token, audio_queue):
    # 对文本进行两次urlencode
    encoded_text = quote(text)
    tts_url = "https://tsn.baidu.com/text2audio"
    params = {
        'tex': encoded_text,
        'tok': token,
        'cuid': 'GPT-3-Client',
        'ctp': 1,
        'lan': 'zh',
        'spd': 6,
        'pit': 5,
        'vol': 2,
        'per': 1,
        'aue': 6
    }
    response = requests.post(tts_url, params=params, stream=True)
    if response.status_code == 200:
        audio_queue.put(response.content)

def play_audio_queue(audio_queue):
    while True:
        audio_data = audio_queue.get()
        if audio_data == "STOP":
            break
        with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as f:
            f.write(audio_data)
            f.flush()
            subprocess.run(['aplay', f.name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
