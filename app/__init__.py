from pathlib import Path
from flask import Flask

instance_path = Path(__file__).parent.parent
app = Flask(__name__, instance_path=instance_path)

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