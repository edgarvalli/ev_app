from os import path
from app import app
from app.tools.utils import load_config


config: dict = load_config()

host = config['host']
port = config['port']
debug = config['debug']


for key in config.keys():
    app.config[key] = config[key]

app.secret_key = config['secret_key']
app.config['models_path'] = path.join(app.root_path, 'models')

if __name__ == '__main__':
    app.run(host=host, port=port, debug=debug)