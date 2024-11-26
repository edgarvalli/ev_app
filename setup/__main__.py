import sys
from pathlib import Path

app_path = Path(__file__).parent.parent
sys.path.insert(0,str(app_path))

# import dbinit

from app.tools.evorm.database import Database

db = Database()
db.config.dbname = 'evapp'

columns = db.get_description_model('users')

print(columns)