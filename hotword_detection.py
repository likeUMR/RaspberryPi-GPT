import os
import json
import pvporcupine
import pyaudio
import struct

def create_detector(access_key, keyword="picovoice"):
    return pvporcupine.create(access_key=access_key, keywords=[keyword])

def get_audio_stream(porcupine):
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )
    return pa, audio_stream

def detect_hotword(porcupine, audio_stream):
    pcm = audio_stream.read(porcupine.frame_length)
    pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
    return porcupine.process(pcm)

def main():
    # 获取当前脚本文件所在的绝对路径
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, 'config.json')
    
    # 从配置文件加载配置
    with open(config_path, 'r') as file:
        config = json.load(file)
    
    # 初始化热词检测器
    porcupine = create_detector(config['porcupine_access_key'], keyword=config.get('porcupine_hot_word', 'picovoice'))
    pa, audio_stream = get_audio_stream(porcupine)
    
    try:
        print("Listening for hotword...")
        while True:
            result = detect_hotword(porcupine, audio_stream)
            if result >= 0:
                print("\rHotword Detected!")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        audio_stream.close()
        pa.terminate()
        porcupine.delete()

if __name__ == '__main__':
    main()
