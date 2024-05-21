import os
import json
from openai import OpenAI
import queue
import threading
from speech_module import get_baidu_token, text_to_speech, play_audio_queue

def initialize_gpt_client(api_key, base_url="https://api.deepseek.com"):
    return OpenAI(api_key=api_key, base_url=base_url)

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
    speech_buffer = ""  # 用于累积文本，直到遇到特定标点
    print("\rAI回复:", end="")
    for resp in response:
        content = resp.choices[0].delta.content
        ai_response_text += content
        print(content, end="")
        
        # 累积内容到speech_buffer，直到遇到特定标点
        speech_buffer += content
        if any(punct in content for punct in ['，', '。','.','!','?']):
            text_to_speech(speech_buffer, token, audio_queue)
            speech_buffer = ""  # 清空buffer

    # 处理剩余的文本（如果有）
    if speech_buffer:
        text_to_speech(speech_buffer, token, audio_queue)

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
