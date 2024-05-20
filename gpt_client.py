import os
import json
from openai import OpenAI
import requests
import subprocess
import tempfile
import queue
import threading

def initialize_gpt_client(api_key, base_url="https://api.deepseek.com"):
    return OpenAI(api_key=api_key, base_url=base_url)

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
    tts_url = "https://tsn.baidu.com/text2audio"
    params = {
        'tex': text,
        'tok': token,
        'cuid': 'GPT-3-Client',
        'ctp': 1,
        'lan': 'zh',
        'spd': 5,
        'pit': 5,
        'vol': 5,
        'per': 0,
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

def process_text(client, conversation_history, input_text, token, audio_queue, MAX_HISTORY_LENGTH=5):
    conversation_history.append({"role": "user", "content": input_text})
    if len(conversation_history) > MAX_HISTORY_LENGTH:
        conversation_history = conversation_history[-MAX_HISTORY_LENGTH:]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=conversation_history,
        stream=True
    )
    
    ai_response_text = ""
    print("\rAI回复:", end="")
    for resp in response:
        content = resp.choices[0].delta.content
        ai_response_text += content
        print(content, end="")
        text_to_speech(content, token, audio_queue)
    print()

    conversation_history.append({"role": "assistant", "content": ai_response_text})
    return ai_response_text

def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, 'config.json')
    
    with open(config_path, 'r') as file:
        config = json.load(file)
    
    gpt_client = initialize_gpt_client(
        api_key=config['openai_api_key'],
        base_url=config['openai_base_url']
    )
    baidu_token = get_baidu_token(config['baidu_api_key'], config['baidu_secret_key'])
    audio_queue = queue.Queue()
    audio_thread = threading.Thread(target=play_audio_queue, args=(audio_queue,))
    audio_thread.start()
    
    MAX_HISTORY_LENGTH = config.get('max_history_length', 5)
    conversation_history = []

    print("Enter 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            audio_queue.put("STOP")
            audio_thread.join()
            break

        ai_response = process_text(gpt_client, conversation_history, user_input, baidu_token, audio_queue, MAX_HISTORY_LENGTH)

if __name__ == '__main__':
    main()
