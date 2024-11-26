import ast
import importlib
from pathlib import Path
from app.tools.evorm import Database
from flask import Blueprint, request, current_app


class HttpAPIResponse:

    error: bool
    message: str
    data: list | dict

    def __init__(self) -> None:
        self.error = True
        self.message = "Http Response Init"
        self.data = {}

    def todict(self) -> dict:
        return self.__dict__


api = Blueprint("api", import_name=__name__, url_prefix="/api")


@api.route("/")
def api_index():
    r = HttpAPIResponse()
    return r.todict()


@api.route("/db/<dbname>")
def api_new_db(dbname):

    from app.tools.evorm import DBConfig, generate_database

    config = DBConfig()
    config.parse_from_dict(current_app.config)
    config.dbname = config.dbprefix + "_" + dbname
    models_path = Path(current_app.root_path).joinpath("models")
    return generate_database(config=config, models_path=models_path)


@api.route("/<model>/search/")
def api_search(model):
    fields = request.args.get("fields", "*")
    where = request.args.get("where", None)
    limit = request.args.get("limit", "50")

    if where:
        where = ast.literal_eval(where)
    db = Database()
    db.config.parse_from_dict(current_app.config)
    return db.search(model=model, where=where, fields=fields, limit=limit)

@api.route('/<model>/update', methods=['PUT'])
def api_update(model):
    json_body: dict = request.get_json()
    if json_body is None:
        return {"error": "Invalid or missing JSON"}, 400
    
    id = json_body.get('id', 0)
    data = json_body.get('data',{})
    db = Database()
    db.config.parse_from_dict(current_app.config)
    db.config.dbname = request.headers.get('dbname','evapp')
    
    db.update(model=model, id=id, data=data)
    
    return {}

@api.route("/<model>/<method>", methods=["POST", "GET", "UPDATE", "DELETE"])
def api_find(model, method):
    try:
        if request.method == "GET":
            key = "args"
        else:
            if request.form:
                key = "form"
            else:
                key = "json"

        data: dict = getattr(request, key)

        module = f"app.modules.{model}"
        module = importlib.import_module(module)
        module = getattr(module, model)
        module = module()
        setattr(module, "dbname", "dbname")
        return getattr(module, method)(data)
    except ModuleNotFoundError as e:
        return {"error": True, "message": e.name}
    except TypeError as e:
        return {"error": True, "message": e.args[0]}
    except:
        return {"error": True, "message": "Something wrong"}
