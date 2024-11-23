from app.tools import load_modules
import json
from app import app

file_config = open('config.json', 'r')
config_json = file_config.read()
file_config.close()

config: dict = json.loads(config_json)

host = config['host']
port = config['port']
debug = config['debug']


for key in config.keys():
    app.config[key] = config[key]

app.secret_key = config['secret_key']

load_modules(app=app)

if __name__ == '__main__':    
    app.run(host=host, port=port, debug=debug)