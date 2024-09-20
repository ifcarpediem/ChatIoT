import json
import pyaudio
import wave
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__)))

CHUNK = 2048

def get_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def play_audio(wave_input_path):
    p = pyaudio.PyAudio()
    wf = wave.open(wave_input_path, 'rb')
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(CHUNK)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    p.terminate()

def play_wakeup():
    resource_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'voice_ui','resource')
    wakeup_audio_path = os.path.join(resource_path, 'wav/wakeup_audio/zaine.wav')
    play_audio(wakeup_audio_path)