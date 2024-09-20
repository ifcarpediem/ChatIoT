import json
import yaml

def get_json(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def write_json(file_path: str, data: dict):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_yaml(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)
    
def write_yaml(file_path: str, data: dict):
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)

def append_file(file_path: str, data: str):
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(data)
    
if __name__ == '__main__':
    pass