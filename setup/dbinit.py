from pathlib import Path
from app.tools.evschema import Database, generate_database, DBConfig
from app.tools import utils

config = DBConfig()
config.parse_from_dict(utils.load_config())

current_path = Path(__file__).parent
models_path = current_path.joinpath('models')

print(models_path)

generate_database(config=config, models_path=models_path)

db = Database()
db.config = config
print('Loading default data......')
csv_path_files = current_path.joinpath('data')

for item in csv_path_files.iterdir():
    db.bulk_from_csv(item.absolute())
