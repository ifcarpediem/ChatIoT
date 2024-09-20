import subprocess
from config import CONFIG

port = CONFIG.configs["web_ui"]["port"]

def main():
    subprocess.run(["streamlit", "run", f"--server.port={port}", "./frontend/web_ui.py"])

if __name__ == '__main__':
    main()