import ast
import hashlib
import importlib
from functools import wraps
from app.tools import jwt_tool
from app.tools.utils import generate_password
from app.tools.evschema import Database
from marshmallow import fields, Schema, ValidationError
from flask import Blueprint, request, current_app, make_response, Response


def set_response(payload: dict) -> Response:
    
        access_token = jwt_tool.access_token(payload=payload)
        refresh_token = jwt_tool.refresh_token(payload=payload)

        payload['fingerprint'] = generate_password(size=20)
        
        response = make_response(payload)
        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            secure=False,
            expires= 15 * 60
        )
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=False,
            expires=(7 * (60 * 24)) * 60
        )
        
        return response

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


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    rfc = fields.Str()


def validate_input(schema, data):
    try:
        return schema.load(data)
    except ValidationError as e:
        return {"error": True, "message": e.messages}, 400


def auth_api_middleware(func):
    @wraps(func)
    def middleware(*args, **kvargs):
        token = request.cookies.get("access_token")
        if not token:
            
            refresh_token = request.cookies.get('refresh_token')
            
            if not refresh_token:
                return {"error": True, "message": "Token missing"}, 401
            else:
                try:
                    payload = jwt_tool.decode_refresh_token(refresh_token)
                    request.user = payload
                    access_token = jwt_tool.access_token(payload)
                    response = make_response(func(*args, **kvargs))
                    response.set_cookie(
                        "access_token",
                        access_token,
                        httponly=True,
                        secure=False,  # Asegúrate de que esto sea True en producción
                        expires= 15 * 60
                    )
                    return response
                except jwt_tool.jwt.PyJWTError as e:
                    print(e)
                    return {"error": True, "message": "Invalid refresh token"}, 401

        try:
            payload = jwt_tool.decode_access_token(token)
            request.user = payload  # Asocia el usuario al request
        except jwt_tool.jwt.PyJWTError as e:
            print(e)
            return {"error": True, "message": "Invalid token"}, 401

        return func(*args, **kvargs)

    return middleware


def initdb() -> Database:
    db = Database()
    db.config.parse_from_dict(current_app.config)
    db.config.dbname = request.headers.get("dbname", current_app.config["dbname"])

    return db


api = Blueprint("api", import_name=__name__, url_prefix="/api")


@api.route("/")
def api_index():
    r = HttpAPIResponse()
    return r.todict()


@api.route("/login", methods=["POST"])
def api_login():

    schema = LoginSchema()
    
    print(request.origin)
    
    if request.headers['content-type'] == 'application/json':
        data = request.json
    else:
        data = request.form
    
    validated_data = validate_input(schema, data=data)

    if isinstance(validated_data, tuple):
        return validated_data

    username = validated_data["username"]
    password = validated_data["password"]
    rfc: str = str(current_app.config['dbname']).upper()
    
    if "rfc" in validated_data:
        rfc = validated_data["rfc"]

    def make_error_response(key: str = "val", msg: str = None):
        return {"error": True, "message": msg if msg else f"Debe de ingresar un {key}"}


    db = initdb()

    query = "SELECT id,email,company_name,name,rfc FROM customers WHERE rfc=%s and active=1"
    exists = db.query(query=query, rfc=rfc).fetchone()

    if exists is None:
        query = "SELECT id,email,fullname,is_admin,password,username FROM users WHERE username=%s"
        exists = db.query(query=query, username=username).fetchone()
        if exists is None:
            return make_error_response(msg="El usuario no existe")

        query_result_password = exists["password"]
        password: hashlib._Hash = hashlib.sha256(str(password).encode("utf-8"))

        if password.hexdigest() == query_result_password:

            del exists["password"]            
            return set_response(exists)

        else:
            return make_error_response(msg="Password incorrecto")

    else:
        query = f"SELECT id,email,fullname,is_admin,password,username FROM users WHERE username=%s"
        db.changedb(current_app.config["dbprefix"] + "_" + rfc)
        exists = db.query(query=query, username=username).fetchone()

        if exists is None:
            return make_error_response(msg="El usuario no existe")

        query_result_password = exists["password"]
        password: hashlib._Hash = hashlib.sha256(str(password).encode("utf-8"))

        if password.hexdigest() == query_result_password:

            del exists["password"]
            return set_response(exists)

        else:
            return make_error_response(msg="Password incorrecto")


@api.route("/<model>/search")
@auth_api_middleware
def api_search(model: str):
    fields = request.args.get("fields", "*")
    where = request.args.get("where", None)
    limit = request.args.get("limit", "50")

    if where:
        where = ast.literal_eval(where)

    db = initdb()
    return db.search(model=model, where=where, fields=fields, limit=limit)


@api.route("/<model>/update/<id>", methods=["PUT"])
@auth_api_middleware
def api_update(model: str, id: int):

    data: dict = {}
    content_type = request.headers.get("content-type")

    if content_type == "application/json":
        data = request.json
    else:
        data = request.form

    db = initdb()

    return db.update(model=model, id=int(id), data=data)


@api.route("/<model>/save", methods=["POST"])
@auth_api_middleware
def api_save(model: str):
    data: dict = {}
    content_type = request.headers.get("content-type")

    if content_type == "application/json":
        data = request.json
    else:
        data = request.form

    db = initdb()
    return db.save(model=model, record=data)


@api.route("/<model>/unlink/<id>")
@auth_api_middleware
def api_unlink(model, id):
    db = initdb()
    return db.unlink(model=model, id=id)


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
