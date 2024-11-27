import json
import string
import inspect
import secrets
import importlib
from pathlib import Path
from app.tools.evschema.database import Database

def is_bidimensional(tup):
    return isinstance(tup, tuple) and all(isinstance(i, (tuple, list)) for i in tup)

def load_modules():
    
    
    #Init loading
    models_path = root_path().joinpath('app', 'models')
    db = Database()
    db.config.parse_from_dict(load_config())
    data: list[dict] = []
    
    for path in models_path.iterdir():
        if '__pycache__' == path.name or '__init__.py' == path.name:
            continue
        model_name = path.name[:-3]
        
        models = importlib.import_module(f'app.models.{model_name}')
        models = inspect.getmembers(models, inspect.isclass)
        
        for desc,model in models:
            if hasattr(model, 'build'):
                model = model()
                model_name = model._name
                if hasattr(model, '_description'):
                    desc = model._description
                
                data.append({
                    'name': model_name,
                    'description': desc,
                    'active': 1
                })
        
    return db.bulk('models', data)

def root_path() -> Path:
    root_path = Path(__file__).parent
    root_path = root_path.parent.parent
    return root_path

def load_config() -> dict:
    file_path = root_path()
    file_path = file_path.joinpath('config.json')
    file_config = open(file_path, 'r')
    config_json = file_config.read()
    file_config.close()
    config: dict = json.loads(config_json)
    return config

def set_config(key: str, val: str):
    config: dict = load_config()
    config[key] = val
    file_path = root_path()
    file_path = file_path.joinpath('config.json')
    file_config = open(file_path, 'w')
    file_config.write(json.dumps(config))
    file_config.close()
    
def generate_password(length=12):
    # Caracteres posibles para la contraseña
    caracteres = string.ascii_letters + string.digits + string.punctuation  # Letras, números y signos
    # Generar una contraseña aleatoria usando 'secrets' para mayor seguridad
    contraseña = ''.join(secrets.choice(caracteres) for i in range(length))
    return contraseña