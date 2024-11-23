import sys
from os import path
import importlib.util as importutil
from types import ModuleType

def importmodule(module_name:str, module_path: str) -> ModuleType:
    
    if not path.exists(module_path):
        return None
    
    
    print(module_path)
    spec = importutil.spec_from_file_location(module_name, module_path)
    
    if spec is None:
        return None
    
    module = importutil.module_from_spec(spec=spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module=module)
    
    return module