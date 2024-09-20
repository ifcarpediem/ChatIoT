import sys
sys.path.append("./frontend/voice_ui/tencent")
import os
cwd = os.getcwd()
sys.path.append(cwd)

import time
from datetime import datetime
import json
from frontend.voice_ui.tencent.common import credential
from frontend.voice_ui.tencent.common.log import logger
# asr
from frontend.voice_ui.tencent.asr import speech_recognizer
# tts
import wave
from frontend.voice_ui.tencent.tts import speech_synthesizer_ws
from config import CONFIG

# base config
APPID = CONFIG.configs["tencent"]["appid"]
SECRET_ID = CONFIG.configs["tencent"]["secret_id"]
SECRET_KEY = CONFIG.configs["tencent"]["secret_key"]

# asr
ENGINE_MODEL_TYPE = "16k_zh"
SLICE_SIZE = 6400

# tts
VOICETYPE = 1004 # 音色类型
CODEC = "pcm" # 音频格式：pcm/mp3
SAMPLE_RATE = 16000 # 音频采样率：8000/16000
ENABLE_SUBTITLE = True
EMOTION_CATEGORY = "" # 仅支持多情感音色
EMOTION_INTENSITY = 100
SPEED = 1


class MySpeechRecognitionListener(speech_recognizer.SpeechRecognitionListener):
    def __init__(self, id):
        self.id = id
        self.final_result = ""

    def on_recognition_start(self, response):
        logger.info("%s|%s|OnRecognitionStart\n" % (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), response['voice_id']))

    def on_sentence_begin(self, response):
        rsp_str = json.dumps(response, ensure_ascii=False)
        logger.info("%s|%s|OnRecognitionSentenceBegin, rsp %s\n" % (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), response['voice_id'], rsp_str))

    def on_recognition_result_change(self, response):
        rsp_str = json.dumps(response, ensure_ascii=False)
        logger.info("%s|%s|OnResultChange, rsp %s\n" % (datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"), response['voice_id'], rsp_str))

    def on_sentence_end(self, response):
        rsp_str = json.dumps(response, ensure_ascii=False)
        logger.info("%s|%s|OnSentenceEnd, rsp %s\n" % (datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"), response['voice_id'], rsp_str))
        self.final_result = response['result']['voice_text_str']

    def on_recognition_complete(self, response):
        logger.info("%s|%s|OnRecognitionComplete\n" % (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), response['voice_id']))

    def on_fail(self, response):
        rsp_str = json.dumps(response, ensure_ascii=False)
        logger.info("%s|%s|OnFail,message %s\n" % (datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"), response['voice_id'], rsp_str))

class MySpeechSynthesisListener(speech_synthesizer_ws.SpeechSynthesisListener):
    
    def __init__(self, id, codec, sample_rate):
        self.start_time = time.time()
        self.id = id
        self.codec = codec.lower()
        self.sample_rate = sample_rate

        self.audio_file = ""
        self.audio_data = bytes()
    
    def set_audio_file(self, filename):
        self.audio_file = filename

    def on_synthesis_start(self, session_id):
        '''
        session_id: 请求session id，类型字符串
        '''
        super().on_synthesis_start(session_id)
        
        # TODO 合成开始，添加业务逻辑
        if not self.audio_file:
            self.audio_file = "speech_synthesis_output." + self.codec
        self.audio_data = bytes()

    def on_synthesis_end(self):
        super().on_synthesis_end()

        # TODO 合成结束，添加业务逻辑
        logger.info("write audio file, path={}, size={}".format(
            self.audio_file, len(self.audio_data)
        ))
        if self.codec == "pcm":
            wav_fp = wave.open(self.audio_file, "wb")
            wav_fp.setnchannels(1)
            wav_fp.setsampwidth(2)
            wav_fp.setframerate(self.sample_rate)
            wav_fp.writeframes(self.audio_data)
            wav_fp.close()
        elif self.codec == "mp3":
            fp = open(self.audio_file, "wb")
            fp.write(self.audio_data)
            fp.close()
        else:
            logger.info("codec {}: sdk NOT implemented, please save the file yourself".format(
                self.codec
            ))

    def on_audio_result(self, audio_bytes):
        '''
        audio_bytes: 二进制音频，类型 bytes
        '''
        super().on_audio_result(audio_bytes)
        
        # TODO 接收到二进制音频数据，添加实时播放或保存逻辑
        self.audio_data += audio_bytes

    def on_text_result(self, response):
        '''
        response: 文本结果，类型 dict，如下
        字段名       类型         说明
        code        int         错误码（无需处理，SpeechSynthesizer中已解析，错误消息路由至 on_synthesis_fail）
        message     string      错误信息
        session_id  string      回显客户端传入的 session id
        request_id  string      请求 id，区分不同合成请求，一次 websocket 通信中，该字段相同
        message_id  string      消息 id，区分不同 websocket 消息
        final       bool        合成是否完成（无需处理，SpeechSynthesizer中已解析）
        result      Result      文本结果结构体

        Result 结构体
        字段名       类型                说明
        subtitles   array of Subtitle  时间戳数组
        
        Subtitle 结构体
        字段名       类型     说明
        Text        string  合成文本
        BeginTime   int     开始时间戳
        EndTime     int     结束时间戳
        BeginIndex  int     开始索引
        EndIndex    int     结束索引
        Phoneme     string  音素
        '''
        super().on_text_result(response)

        # TODO 接收到文本数据，添加业务逻辑
        result = response["result"]
        subtitles = []
        if "subtitles" in result and len(result["subtitles"]) > 0:
            subtitles = result["subtitles"]

    def on_synthesis_fail(self, response):
        '''
        response: 文本结果，类型 dict，如下
        字段名 类型
        code        int         错误码
        message     string      错误信息
        '''
        super().on_synthesis_fail(response)

        # TODO 合成失败，添加错误处理逻辑
        err_code = response["code"]
        err_msg = response["message"]

class tencent_asr_tts_service():
    def __init__(self):
        self.credential_var = credential.Credential(SECRET_ID, SECRET_KEY)
        # asr
        self.listener_asr = MySpeechRecognitionListener(id)
        self.recognizer = speech_recognizer.SpeechRecognizer(
            APPID, self.credential_var, ENGINE_MODEL_TYPE,  self.listener_asr)
        
        # tts
        self.listener_tts = MySpeechSynthesisListener(id, CODEC, SAMPLE_RATE)
        self.synthesizer = speech_synthesizer_ws.SpeechSynthesizer(
            APPID, self.credential_var, self.listener_tts)
        
    def asr(self, audio):
        self.recognizer.set_filter_modal(1)
        self.recognizer.set_filter_punc(1)
        self.recognizer.set_filter_dirty(1)
        self.recognizer.set_need_vad(1)
        #recognizer.set_vad_silence_time(600)
        self.recognizer.set_voice_format(1)
        self.recognizer.set_word_info(1)
        #recognizer.set_nonce("12345678")
        self.recognizer.set_convert_num_mode(1)
        try:
            self.recognizer.start()
            with open(audio, 'rb') as f:
                content = f.read(SLICE_SIZE)
                while content:
                    self.recognizer.write(content)
                    content = f.read(SLICE_SIZE)
        except Exception as e:
            logger.info(e)
        finally:
            self.recognizer.stop()
            return self.listener_asr.final_result
    
    def tts(self, text, audio_path):
        self.listener_tts.set_audio_file(audio_path)
        self.synthesizer.set_text(text)
        self.synthesizer.set_voice_type(VOICETYPE)
        self.synthesizer.set_codec(CODEC)
        self.synthesizer.set_sample_rate(SAMPLE_RATE)
        self.synthesizer.set_enable_subtitle(ENABLE_SUBTITLE)
        if EMOTION_CATEGORY != "":
            self.synthesizer.set_emotion_category(EMOTION_CATEGORY)
            if EMOTION_INTENSITY != 0:
                self.synthesizer.set_emotion_intensity(EMOTION_INTENSITY)  
        self.synthesizer.set_speed(SPEED)
        self.synthesizer.start()
        # wait for processing complete
        self.synthesizer.wait()

if __name__ == "__main__":
    asr_tts = tencent_asr_tts_service()
    # test tts
    text = "欢迎使用腾讯云实时语音合成"
    audio_path = "./temp/test_tts.wav"
    asr_tts.tts(text, audio_path)
    # test asr
    audio = "./temp/test_tts.wav"
    result = asr_tts.asr(audio)
    print(result)

