import importlib.util
import sys
import inspect
import importlib
from pathlib import Path
from .database import Database, DBConfig

def generate_database(config: DBConfig, models_path: str | Path):

    response = {'error': True, 'message': ''}

    if isinstance(models_path, str):
        models_path: Path = Path(models_path)

    if not models_path.is_dir():
        response['message'] = f'It is not a directory. ({models_path})'
        return response
    if not models_path.exists():
        response['message'] = "The path doesn't exist."
        return response

    db = Database()
    db.config = config

    print(f"Creating database with name {db.config.dbname}")
    db.new_database(db.config.dbname)
    for model in models_path.iterdir():
        if model.name == "__pycache__":
            continue

        if model.name == '__ini__.py':
            continue

        model_name = model.name[:-3]

        # Importing module dinamiclly
        spec = importlib.util.spec_from_file_location(model_name, model.absolute())
        module = importlib.util.module_from_spec(spec=spec)
        sys.modules[model_name] = module
        spec.loader.exec_module(module)

        modules = inspect.getmembers(module, inspect.isclass)
        for _, obj in modules:
            # Check if class has 'build' method
            if hasattr(obj, "build") and callable(getattr(obj, "build", None)):
                class_obj = obj()  # Instantiate the class
                action = getattr(class_obj, "build")
                action(config)  # Call the 'build' method

        response["message"] = (
            f"Database {db.config.dbname} and models created successfully."
        )
    return response


def create_database(config: DBConfig, models_path: str) -> dict:
    return_obj = {"error": True, "message": ""}
    models_path: Path = Path(models_path)

    if not models_path.exists() or not models_path.is_dir():
        print("Path is no directory or not exists!!")
        return_obj["message"] = f"Path is no directory or not exists!! ({models_path})"
        return return_obj

    db = Database()
    db.config = config

    print(f"Creating database with name {db.config.dbname}")
    db.new_database(db.config.dbname)

    for model in models_path.iterdir():

        if model.name == "__pycache__":
            continue

        if model.name.startswith("__ini__"):
            continue

        if model.name.endswith(".py"):
            model_name = model.name[:-3]

        try:
            # Importar dinámicamente el módulo
            module = importlib.import_module(f"app.models.{model_name}")
        except ImportError as e:
            print(f"Error al importar el módulo {model_name}: {e}")
            continue

        modules = inspect.getmembers(module, inspect.isclass)

        for name, obj in modules:
            # Check if class has 'build' method
            if hasattr(obj, "build") and callable(getattr(obj, "build", None)):
                class_obj = obj()  # Instantiate the class
                action = getattr(class_obj, "build")
                action(config)  # Call the 'build' method

    return_obj["message"] = (
        f"Database {db.config.dbname} and models created successfully."
    )
    return return_obj
