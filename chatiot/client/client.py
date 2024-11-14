import subprocess
from config import CONFIG

port = CONFIG.configs["web_ui"]["port"]

def main():
    # subprocess.run(["streamlit", "run", f"--server.port={port}", "./frontend/web_ui.py"])
    # python运行chatiot\client\frontend\client_fastapi.py
    subprocess.run(["python", "./frontend/client_fastapi.py"])
    

if __name__ == '__main__':
    main()