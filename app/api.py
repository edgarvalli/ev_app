import importlib
from flask import Blueprint, request
from app.models import HttpAPIResponse

api = Blueprint("api", import_name=__name__, url_prefix="/api")


@api.route("/")
def api_index():
    r = HttpAPIResponse()
    return r.todict()


@api.route("/<model>/<method>", methods=["POST", "GET", "UPDATE", "DELETE"])
def api_search(model, method):
    try:
        if request.method == "GET":
            key = "args"
        else:
            if request.form:
                key = "form"
            else:
                key = "json"

        data: dict = getattr(request, key)
        # model = data.get("model", "base")
        # method = data.get("method", "search")

        module = f"app.modules.{model}"
        module = importlib.import_module(module)
        module = getattr(module, model)
        module = module()
        setattr(module,'dbname', 'dbname')
        return getattr(module, method)(data)
    except ModuleNotFoundError as e:
        return {"error": True, "message": e.name}
    except TypeError as e:
        return {"error": True, "message": e.args[0]}
    except:
        return {"error": True, "message": "Something wrong"}