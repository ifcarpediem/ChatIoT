import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed

def run_script(script_name):
    process = subprocess.Popen(['python', script_name])
    return process.wait()

def main():
    with ProcessPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(run_script, script) for script in ['llm_service_api.py']]
        for future in as_completed(futures):
            pass

if __name__ == '__main__':
    main()