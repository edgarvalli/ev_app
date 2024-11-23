from flask import Flask

app = Flask(__name__)

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