## Deploy Locally（not recommended now）

### Installation
> Ensure that Python 3.10+ is installed on your system. You can check this by using: `python --version`.

#### Download ChatIoT
Download ChatIoT and ensure that ChatIoT is running on the same device as Home Assistant.
```bash
git clone https://github.com/ifcarpediem/ChatIoT.git
```

#### Start Server
The current server only provides the FastAPI service for Large Language Models (LLMs), with other content updates to follow in the future.

The server-side configuration file is `chatiot/server/configs/config.yaml`, and some parameters are presented as follows:

+ `llm_service`: deploy llm service by FastAPI.
  + `port`: the FastAPI port for the LLM service, default is 10000.
  + `llm_models`: currently supports the GPT series, DeepSeek, and Moonshot. We are working on integrating more LLMs.
    + `api_key`: required


```bash
# start server
cd server
pip install -r requirements.txt
python client.py
```

#### Start Client
The current client is responsible for interacting with the user as well as Home Assistant. Currently, it mainly provides two modes of interaction:

+ Text interaction: You can enter requests on the web page.

<p align="center">
<a href=""><img src="resources\web_ui.png" width="400px"></a>
</p>

+ Voice interaction: You can also interact with the system through voice commands by activating with `jarvis`, requiring the device to have a microphone.

The client-side configuration file is `chatiot/client/configs/config.yaml`, and some parameters are presented as follows:

+ `llm_server`: how to access the llm service
  + `host`: the host of the server
  + `port`: the FastAPI port for the LLM service, default is 10000
  + `model`: select the llm model to use

+ `home_assistant`: how to access Home Assistant
  + `host`: "0.0.0.0", Home Assistant must run on the same device as the client.
  + `port`: default is 8123
  + `token`: the access token
  + `config_path`: the absolute path of Home Assistant's config on this device

+ `porcupine`: the current wake word service is based on [porcupine](https://console.picovoice.ai/login), which provides 'jarvis' by default.
  + `keywords`: []
  + `keyword_paths`:  ["ppn/***"]
  + `sensitivities`: []

+ `tencent`: the current voice service, such as text-to-speech and speech-to-text, is based on [Tencent's services](https://cloud.tencent.com/product/tts)
  + `appid`
  + `secret_id`
  + `secret_key`

+ `web_ui`: the current web page is implemented using Streamlit. 
  + `port`: default is 8501

```bash
# start client
cd client
pip install -r requirements.txt
python client.py
```

<!-- ## Screenshots -->
<!-- # Todos -->