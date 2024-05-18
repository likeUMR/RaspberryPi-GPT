import speech_recognition as sr
from aip import AipSpeech


def initialize_baidu_client(APP_ID, API_KEY, SECRET_KEY):
    return AipSpeech(APP_ID, API_KEY, SECRET_KEY)

def recognize_speech_from_mic(client, recognizer, microphone):
    with microphone as source:
        print("\r请开始说话...     ",end='')
        recognizer.energy_threshold = 500  # 通过调整能量阈值来消除噪音
        audio = recognizer.listen(source)
    print("\r说话完成           ",end='')
    audio_data = audio.get_wav_data()
    result = client.asr(audio_data, 'wav', 16000, {'dev_pid': 1537})
    if result and result['err_no'] == 0:
        return result['result'][0]
    else:
        print("识别错误:", result.get('err_msg', '无错误信息'))
        return None

def main():
    import os
    import json
    # 获取当前脚本文件所在的绝对路径
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, 'config.json')
    # 从配置文件加载配置
    with open(config_path, 'r') as file:
        config = json.load(file)

    # 初始化百度语音识别客户端
    client = initialize_baidu_client(
        config['baidu_app_id'],
        config['baidu_api_key'],
        config['baidu_secret_key']
    )
    
    recognizer = sr.Recognizer()
    microphone = sr.Microphone(sample_rate=16000)

    recognized_text = recognize_speech_from_mic(client, recognizer, microphone)
    if recognized_text:
        print("\r识别到的文本:", recognized_text)
    else:
        print("\r没有识别到文本。")

if __name__ == '__main__':
    main()
