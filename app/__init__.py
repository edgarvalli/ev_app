from flask import Flask
from app.tools.utils import generate_password
from pathlib import Path
instance_path = Path(__file__).parent.parent
app = Flask(__name__, instance_path=instance_path)

app.config['JWT_SECRET_KEY'] = 'RooX9+JFgv?XMGH'
app.config['JWT_REFRESH_SECRET_KEY'] = 'vTTw.1?M*3y)d@UCz*Bg'

from app.api import api
from app.controllers import admin_login_app

app.register_blueprint(api)
app.register_blueprint(admin_login_app)

@app.route('/')
def index():
    return 'Server running on port ' + str(app.config['port'])

@app.route('/test')
def test():
    # module = get_module('admin', 'Users')
    return 'Test'