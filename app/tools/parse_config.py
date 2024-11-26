import json
from pathlib import Path
from os import path

def get_config() -> dict:
    file_path = Path(path.dirname(__file__))
    file_path = file_path.parent.parent
    file_path = file_path.joinpath('config.json')
    file_config = open(file_path, 'r')
    config_json = file_config.read()
    file_config.close()
    config: dict = json.loads(config_json)
    return config