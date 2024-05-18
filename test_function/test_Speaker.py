from playsound import playsound
import os

# 获取当前脚本文件所在的绝对路径
dir_path = os.path.dirname(os.path.realpath(__file__))
sound_path = os.path.join(dir_path, 'test_audio.wav')
playsound(sound_path)
