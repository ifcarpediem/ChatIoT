import sys
from pathlib import Path
cwd = Path.cwd()
sys.path.append(str(cwd))

import streamlit as st
from streamlit_chatbox import *
import os
from frontend.utils.logs import logger
from frontend.voice_ui.wakeup import WakeupHandler
from frontend.voice_ui.tencent_tts_asr import tencent_asr_tts_service
from frontend.utils.utils import play_wakeup, play_audio
from config import CONFIG
from backend.agents.jarvis import JARVIS

wakeup_handler = WakeupHandler()
asr_tts = tencent_asr_tts_service()

temp_input_audio = './temp/input.wav'
temp_output_audio = './temp/output.wav'

current_path = os.path.dirname(__file__)
resource_path = os.path.join(current_path, "web_ui_resource")

chat_box = ChatBox(
    chat_name="ChatIoT",
    user_avatar = os.path.join(resource_path, "user.png"),
    assistant_avatar=os.path.join(resource_path, "assistant.png"),
)

st.set_page_config(
    "ChatIoT",
    initial_sidebar_state="expanded",
    menu_items={'About': f"Welcome to use ChatIoT!"}
)

llm_models = ["gpt-3.5-turbo-0125", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini", "deepseek-chat", "moonshot-v1-8k"]

default_model = llm_models[0]

if not chat_box.chat_inited:
    st.toast(f"Welcome to use ChatIoT!\n Current llm model is `{default_model}`.")

chat_box.init_session()

with st.sidebar:
    st.markdown(""" 
        <style>  
        .title-font {  
            font-size:40px !important;  
            text-align: center;
        }  
        </style>  
        """, unsafe_allow_html=True) 
    st.markdown('<p class="title-font">ChatIoT</p>', unsafe_allow_html=True)
    st.markdown("""  
        <style>  
        .big-font {  
            font-size:30px !important;  
        }  
        </style>  
        """, unsafe_allow_html=True)  
    st.markdown('<p class="big-font">Welcome to use ChatIoT to manage your smart home!</p>', unsafe_allow_html=True)  
    st.divider()
    llm_model = st.sidebar.selectbox("Choose llm model", llm_models, index=0)
    CONFIG.configs['model'] = llm_model
    st.divider()
    st.sidebar.subheader("Home Information")
    hass_host = CONFIG.configs["home_assistant"]["host"]
    hass_port = CONFIG.configs["home_assistant"]["port"]
    device_details_url = f"http://{hass_host}:{hass_port}/"
    st.sidebar.markdown(f'<a href="{device_details_url}" target="_blank">Home Assistant</a>', unsafe_allow_html=True)

if "completed" not in st.session_state:
    st.session_state.completed = True

query = st.chat_input("Say something to Jarvis...")
chat_box.output_messages()

logger.info('Web_ui is running...')

while True:

    if not st.session_state.completed:
        if not query:
            logger.info('waiting user say...')
            play_wakeup()
            logger.info('start recording...')
            wakeup_handler.record_audio_dynamic(temp_input_audio, 100000, 32000)
            logger.info('recorded')
            asr_result = asr_tts.asr(temp_input_audio)
            logger.info('user said: %s' % asr_result)
            query = asr_result

    else:
        keyword = wakeup_handler.run_detect_wakeup_word()
        if not keyword and not query:
            continue
        if not query:
            logger.info('waiting user say...')
            play_wakeup()
            logger.info('start recording...')
            wakeup_handler.record_audio_dynamic(temp_input_audio, 100000, 32000) # TODO
            logger.info('recorded')
            asr_result = asr_tts.asr(temp_input_audio)
            logger.info('user said: %s' % asr_result)
            query = asr_result

    chat_box.user_say(query)
    elements = chat_box.ai_say(
        [
            Markdown("thinking", in_expander=True, expanded=False, title="")
        ]
    )
    res_text, complete_flag = JARVIS.run(query)
    if complete_flag:
        st.session_state.completed = True
    else:
        st.session_state.completed = False
    asr_tts.tts(res_text, temp_output_audio)
    play_audio(temp_output_audio)
    logger.info('assistant said: %s' % res_text)
    chat_box.update_msg(res_text, element_index=0, streaming=False, expanded=True, state="complete")
