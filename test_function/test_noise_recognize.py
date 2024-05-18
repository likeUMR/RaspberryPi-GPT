import speech_recognition as sr

recognizer = sr.Recognizer()
mic = sr.Microphone()

with mic as source:
    print("Adjusting for ambient noise...")
    recognizer.adjust_for_ambient_noise(source, duration=5)  # 增加持续时间以获取更准确的读数
    print("Calculated energy threshold:", recognizer.energy_threshold)
