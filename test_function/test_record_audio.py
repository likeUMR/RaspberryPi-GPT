import pyaudio
import wave

def record_audio(duration=3, output_filename="output.wav"):
    # 设置音频参数
    FORMAT = pyaudio.paInt16  # 数据格式
    CHANNELS = 1              # 单声道
    RATE = 44100              # 采样率
    CHUNK = 1024              # 缓冲区大小
    RECORD_SECONDS = duration # 录音时间
    WAVE_OUTPUT_FILENAME = output_filename

    # 初始化PyAudio对象
    p = pyaudio.PyAudio()

    # 打开音频流
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []

    # 读取数据
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    # 停止录音
    stream.stop_stream()
    stream.close()
    p.terminate()

    # 保存文件
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

if __name__ == "__main__":
    # 获取当前脚本文件所在的绝对路径
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sound_path = os.path.join(dir_path, "recorded_audio.wav")
    print("Recording audio...")
    record_audio(5, sound_path)
