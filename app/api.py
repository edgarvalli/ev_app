import ast
import hashlib
import importlib
from app.tools import jwt_tool
from functools import wraps
from app.tools.evschema import Database, generate_database, DBConfig
from flask import Blueprint, request, current_app, make_response


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


def auth_api_middleware(func):

    @wraps(func)
    def middleware(*args, **kvargs):
        user_agent = request.cookies
        print(user_agent)
        return func(*args, **kvargs)

    return middleware


def initdb() -> Database:
    db = Database()
    db.config.parse_from_dict(current_app.config)
    db.config.dbname = request.headers.get("dbname", current_app.config["dbname"])

    return db


api = Blueprint("api", import_name=__name__, url_prefix="/api")


@api.route('/<db>/create')
def api_create_db(db):
    from pathlib import Path
    
    # models_path = Path(current_app.root_path).joinpath('models')
    config = DBConfig()
    config.parse_from_dict(current_app.config)
    config.dbname = current_app.config['dbprefix'] + '_' + db
    # generate_database(config=config, models_path=models_path)
    return 'Works'
    
@api.route("/")
def api_index():
    r = HttpAPIResponse()
    return r.todict()


@api.route("/login", methods=["POST"])
def api_login():

    data: dict = {}
    content_type = request.headers.get("content-type")

    if content_type == "application/json":
        data = request.json
    else:
        data = request.form

    rfc = data.get("rfc", None)
    username = data.get("username", None)
    password: str = data.get("password", None)

    def make_error_response(key: str = "val", msg: str = None):
        return {"error": True, "message": msg if msg else f"Debe de ingresar un {key}"}

    if rfc is None:
        return make_error_response("RFC")

    if username is None:
        return make_error_response("Usuario")

    if password is None:
        return make_error_response("Password")

    db = initdb()

    query = f"SELECT id,email,company_name,name,rfc FROM customers WHERE rfc='{rfc}' and active=1"
    exists = db.query(query=query).fetchone()

    if exists is None:
        query = f"SELECT id,email,fullname,is_admin,password,username FROM users WHERE username='{username}'"
        exists = db.query(query=query).fetchone()
        if exists is None:
            return make_error_response(msg="El usuario no existe")
        
        query_result_password = exists['password']
        password: hashlib._Hash = hashlib.sha256(str(password).encode('utf-8'))
        
        if password.hexdigest() == query_result_password:

            del exists['password']
            
            response = make_response(exists)
            response.set_cookie(
                "access_token", jwt_tool.access_token(exists), httponly=True, secure=True, max_age=15 * 60
            )
            response.set_cookie(
                "refresh_token", jwt_tool.refresh_token(exists), httponly=True, secure=True, max_age=(7 * (60 * 24)) * 60
            )
            return response
        
        else:
            return make_error_response(msg='Password incorrecto')
    
    else:
        query = f"SELECT id,email,fullname,is_admin,password,username FROM users WHERE username='{username}'"
        db.changedb(current_app.config['dbprefix'] + '_' + rfc)
        exists = db.query(query=query).fetchone()
        
        if exists is None:
            return make_error_response(msg="El usuario no existe")
        
        query_result_password = exists['password']
        password: hashlib._Hash = hashlib.sha256(str(password).encode('utf-8'))
        
        if password.hexdigest() == query_result_password:

            del exists['password']
            
            response = make_response(exists)
            response.set_cookie(
                "access_token", jwt_tool.access_token(exists), httponly=True, secure=True, max_age=15 * 60
            )
            response.set_cookie(
                "refresh_token", jwt_tool.refresh_token(exists), httponly=True, secure=True, max_age=(7 * (60 * 24)) * 60
            )
            return response
        
        else:
            return make_error_response(msg='Password incorrecto')


@api.route("/<model>/search/")
@auth_api_middleware
def api_search(model: str):
    fields = request.args.get("fields", "*")
    where = request.args.get("where", None)
    limit = request.args.get("limit", "50")

    if where:
        where = ast.literal_eval(where)

    db = initdb()
    return db.search(model=model, where=where, fields=fields, limit=limit)


@api.route("/<model>/update", methods=["PUT"])
@auth_api_middleware
def api_update(model: str):
    json_body: dict = request.get_json()
    if json_body is None:
        return {"error": "Invalid or missing JSON"}, 400

    id = request.json.get("id", 0)
    data = request.json.get("data", {})
    db = initdb()

    return db.update(model=model, id=id, data=data)


@api.route("/<model>/save", methods=["POST"])
@auth_api_middleware
def api_save(model: str):
    data = request.json.get("data", {})
    db = initdb()
    return {}


@api.route("/<model>/<method>", methods=["POST", "GET", "UPDATE", "DELETE"])
@auth_api_middleware
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
