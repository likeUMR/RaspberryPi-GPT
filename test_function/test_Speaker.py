import os

# 获取当前脚本文件所在的绝对路径
dir_path = os.path.dirname(os.path.realpath(__file__))
sound_path = os.path.join(dir_path, 'test_audio.wav')

# 使用 aplay 播放音频文件
os.system(f'aplay {sound_path}')
