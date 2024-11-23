import os
import sys
import flask
import inspect
import importlib
from pathlib import Path
from types import ModuleType


def __load_modules():

    modules_path = Path(os.path.dirname(__file__))
    modules_path = os.path.join(modules_path.parent, "modules")

    all_modules = os.listdir(modules_path)

    for module_name in all_modules:

        if module_name != "__pycache__":
            __import__("app.modules." + module_name)
            module = sys.modules["app.modules." + module_name]
            modules = inspect.getmembers(module, inspect.isclass)
            for module in modules:
                name, obj = module
                if hasattr(obj, "build"):
                    class_obj = obj()
                    action = getattr(class_obj, "build")
                    action()


def load_modules(app: flask.Flask):
    modules_path = Path(os.path.dirname(__file__))
    modules_path = modules_path.parent / "modules"  # More 'pathlib' style

    try:
        all_modules = os.listdir(modules_path)
    except FileNotFoundError:
        print(f"Error: The path '{modules_path}' does not exist.")
        return

    for module_name in all_modules:
        # Check if it's a Python file and not a directory
        if module_name != "__pycache__":

            try:
                # Dynamically import the module
                module = importlib.import_module(
                    f"app.modules.{module_name}"
                )

                # Get all classes from the module
                modules = inspect.getmembers(module, inspect.isclass)

                for name, obj in modules:
                    # Check if class has 'build' method
                    if hasattr(obj, "build"):
                        class_obj = obj(app)  # Instantiate the class
                        action = getattr(class_obj, "build")
                        action()  # Call the 'build' method

            except ModuleNotFoundError as e:
                print(
                    f"Error: Could not import module '{module_name}'. {e}"
                )
            except Exception as e:
                print(
                    f"Error occurred in module '{module_name}': {e}"
                )


def get_module(module_name, class_name) -> ModuleType:

    module = sys.modules["app.modules." + module_name]
    module = [
        m for m in inspect.getmembers(module, inspect.isclass) if m[0] == class_name
    ]
    name, module = module[0]
    module: ModuleType = module()
    module.__name__ = name
    return module
