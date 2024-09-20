import os
import struct
import pyaudio
import pvporcupine
import wave
import json
from frontend.utils.logs import logger
from config import CONFIG

def get_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

class WakeupHandler():
    def __init__(self):
        resource_path = os.path.join(os.path.dirname(__file__), 'resource')
        # self.settings = get_json(os.path.join(resource_path, 'settings.json'))["porcupine"]
        self.settings = CONFIG.configs["porcupine"]
        access_key = self.settings['access_key']
        self.pa = pyaudio.PyAudio()
        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=self.settings['keywords'] if self.settings['keywords'] else False,
            keyword_paths=[os.path.join(resource_path, model_name)
                           for model_name in self.settings['keyword_paths']] if self.settings['keyword_paths'] else False,
            sensitivities=self.settings['sensitivities'] if self.settings['sensitivities'] else [
                0.5]
        )
        self.keywords = self.settings['keywords'] if self.settings['keywords'] else [
            name.split('_')[0] for name in self.settings['keyword_paths']]
        self.audio_stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

    def run_detect_wakeup_word(self):
        pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
        keyword_index = self.porcupine.process(pcm)
        if keyword_index >= 0:
            return self.keywords[keyword_index]
        else:
            return False
        
    def record_audio_time(self, wave_out_path, record_second):
        wf = wave.open(wave_out_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.pa.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.porcupine.sample_rate)
        for _ in range(0, int(self.porcupine.sample_rate * record_second / self.porcupine.frame_length)):
            pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            wf.writeframes(pcm)
        wf.close()

    def record_audio_dynamic(self, wave_out_path, silence_threshold, min_silence_duration):
        wf = wave.open(wave_out_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.pa.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.porcupine.sample_rate)
        recording = False
        silence_frames = 0

        while True:
            pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            
            if not recording:
                # TODO 动态调整阈值
                if self.is_speech(pcm, silence_threshold):
                    recording = True
                    wf.writeframes(pcm)  # 直接写入PCM字节数据
            else:
                wf.writeframes(pcm)
                if self.is_speech(pcm, silence_threshold):
                    silence_frames = 0  # 重置沉默计数器
                else:
                    silence_frames += 1  # 增加沉默计数器

                if silence_frames >= min_silence_duration / self.porcupine.frame_length:
                    break  # 达到最小沉默持续时间，停止录音

        wf.close()

    def is_speech(self, pcm, threshold):
        """
        检测当前帧是否为语音。
        :param pcm: PCM数据。
        :param threshold: 阈值。
        :return: 如果当前帧为语音，则返回True。
        """
        # 计算当前帧的能量
        energy = sum([abs(sample) for sample in struct.unpack_from("h" * self.porcupine.frame_length, pcm)])
        # logger.debug("energy: %f" % energy)
        print("energy: %f" % energy)
        return energy > threshold
    
    def release(self):
        self.porcupine.delete()

