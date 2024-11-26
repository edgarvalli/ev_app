import inspect
import importlib
from pathlib import Path

from app.tools.evorm import Database
from app.tools.utils import Utils

db = Database()
db.config.parse_from_dict(Utils.load_config())

print(f"Creating database with name {db.config.dbname}")
db.new_database(db.config.dbname)


current_path = Path(__file__).parent
models_path = current_path.joinpath('models')
for model in models_path.iterdir():

    if model.name == "__pycache__":
        continue
    
    if model.name.endswith(".py"):
        model_name = model.name[:-3]
        
        
    try:
        # Importar dinámicamente el módulo
        module = importlib.import_module(f"setup.models.{model_name}")
    except ImportError as e:
        print(f"Error al importar el módulo {model_name}: {e}")
        continue

    modules = inspect.getmembers(module, inspect.isclass)

    for name, obj in modules:
        # Check if class has 'build' method
        if hasattr(obj, "build"):
            class_obj = obj()  # Instantiate the class
            action = getattr(class_obj, "build")
            action(db.config)  # Call the 'build' method


print('Saving models availables......')
config = Utils.load_modules()

print('Loading default data......')
csv_path_files = current_path.joinpath('data')

for item in csv_path_files.iterdir():
    db.bulk_from_csv(item.absolute())

print(config)
