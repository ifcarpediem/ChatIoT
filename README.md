ChatIoT: Zero-code Generation of Trigger-action Based IoT Programs
===
The mission of ChatIoT is to empower users to create TAP (Trigger-action Program) through natural language interactions. 

This repository is dedicated to the smart home domain, utilizing the Home Assistant open-source platform as its core infrastructure. Once ChatIoT is deployed, users can effortlessly control smart home devices using natural language (e.g., 'Turn on the lights') or create TAP rules to automate tasks (e.g., 'If someone passes through the living room, automatically turn on the living room lights').

<p align="center">
<a href=""><img src="docs\resources\ChatIoT_usage_overview.png" width="500px"></a>
</p>

# Pre-requisites
You will need to install [Home Assistant](https://www.home-assistant.io/installation/) and integrate your devices with it (the project currently mainly supports devices that use the MIoT protocol, which can be connected through [Xiaomi Miot Auto](https://github.com/al-one/hass-xiaomi-miot)). Please ensure that the device names and areas are correctly configured. Additionally, please mount the Home Assistant configuration file to a local directory (as future configurations will be required).

# Get Started

## Installation
> Ensure that Python 3.9+ is installed on your system. You can check this by using: `python --version`.

### Download ChatIoT
Download ChatIoT and ensure that ChatIoT is running on the same device as Home Assistant.
```bash
git clone https://github.com/ifcarpediem/ChatIoT.git
```

### Start Server
The current server only provides the FastAPI service for Large Language Models (LLMs), with other content updates to follow in the future.

The server-side configuration file is `chatiot/server/configs/config.yaml`, and some parameters are presented as follows:

+ `llm_models`: Currently supports the GPT series, DeepSeek, and Moonshot. We are working on integrating more LLMs.
  + `port`: the FastAPI port for the LLM service, default is 10000.
  + `api_key`: required

```bash
# start server
cd server
pip install -r requirements.txt
python client.py
```

### Start Client
The current client is responsible for interacting with the user as well as Home Assistant. Currently, it mainly provides two modes of interaction:

+ Text interaction: You can enter requests on the web page.

<p align="center">
<a href=""><img src="docs\resources\web_ui.png" width="400px"></a>
</p>

+ Voice interaction: You can also interact with the system through voice commands by activating with `jarvis`, requiring the device to have a microphone.

The client-side configuration file is `chatiot/client/configs/config.yaml`, and some parameters are presented as follows:

+ `llm_server`: How to access the llm service
  + `host`: the host of the server
  + `port`: the FastAPI port for the LLM service, default is 10000
  + `model`: select the llm model to use

+ `home_assistant`: How to access Home Assistant
  + `host`: "0.0.0.0", Home Assistant must run on the same device as the client.
  + `port`: default is 8123
  + `token`: the access token
  + `config_path`: The absolute path of Home Assistant's config on this device

+ `porcupine`: The current wake word service is based on [porcupine](https://console.picovoice.ai/login), which provides 'jarvis' by default.
  + `keywords`: []
  + `keyword_paths`:  ["ppn/***"]
  + `sensitivities`: []

+ `tencent`: The current voice service, such as text-to-speech and speech-to-text, is based on [Tencent's services](https://cloud.tencent.com/product/tts)
  + `appid`
  + `secret_id`
  + `secret_key`

+ `web_ui`: The current web page is implemented using Streamlit. 
  + `port`: default is 8501

```bash
# start client
cd client
pip install -r requirements.txt
python client.py
```

<!-- ## Screenshots -->
<!-- # Todos -->

# Citation
To cite [ChatIoT](https://maestro.acm.org/trk/clickp?ref=z16l2snue3_2-310b8_0x33ae25x01410&doi=3678585) in publications, please use the following BibTeX entries.

```bibtex
@article{gao2024chatiot,
  title={ChatIoT: Zero-code Generation of Trigger-action Based IoT Programs},
  author={Gao, Yi and Xiao, Kaijie and Li, Fu and Xu, Weifeng and Huang, Jiaming and Dong, Wei},
  journal={Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies},
  volume={8},
  number={3},
  pages={1--29},
  year={2024},
  publisher={ACM New York, NY, USA}
}
```



