import speech_recognition as sr
import os
import json
from hotword_detection import create_detector, get_audio_stream, detect_hotword
from speech_to_text import initialize_baidu_client, recognize_speech_from_mic
from gpt_client import initialize_gpt_client, process_text

def main():

    # 获取当前脚本文件所在的绝对路径
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, 'config.json')
    # 从配置文件加载配置
    with open(config_path, 'r') as file:
        config = json.load(file)

    # 初始化 Porcupine 热词检测
    porcupine = create_detector(config['porcupine_access_key'])
    pa, audio_stream = get_audio_stream(porcupine)
    
    # 初始化百度语音识别客户端
    baidu_client = initialize_baidu_client(
        config['baidu_app_id'],
        config['baidu_api_key'],
        config['baidu_secret_key']
    )
    
    # 初始化 OpenAI GPT 客户端
    gpt_client = initialize_gpt_client(
        config['openai_api_key'],
        base_url=config['openai_base_url']
    )
    max_history_length = config.get('max_history_length', 5)
    
    recognizer = sr.Recognizer()
    microphone = sr.Microphone(sample_rate=16000)
    conversation_history = []
    
    try:
        while True:
            print("\rListening for hotword...",end='')
            if detect_hotword(porcupine, audio_stream) >= 0:
                print("\rHotword Detected!     ",end='')
                recognized_text = recognize_speech_from_mic(baidu_client, recognizer, microphone)
                print("\r用户:", recognized_text)
                if recognized_text:
                    response_text = process_text(gpt_client, conversation_history, recognized_text, max_history_length)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        audio_stream.close()
        pa.terminate()
        porcupine.delete()

if __name__ == '__main__':
    main()
