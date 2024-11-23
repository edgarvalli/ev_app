import inspect
from flask import Flask
from app.tools.database import Database


class Model:
    _name: str


    def __init__(self, app: Flask) -> None:
        self.app = app
        
    def build(self) -> None:
        with self.app.app_context():
            self._name = self.get_model_name()
            if not self.check_is_model_exists():
                self.generate_model()
    
    
    def __default_query(self, fields: list[str]) -> str:
        
        all_fields = ["id INT AUTO_INCREMENT PRIMARY KEY"]
        all_fields.extend(fields)
        all_fields.append('create_date DATETIME DEFAULT CURRENT_TIMESTAMP')
        all_fields.append('update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
        query = f"CREATE TABLE IF NOT EXISTS {self._name} ({','.join(all_fields)})"
        return query

    def check_is_model_exists(self):
        dbname = self.app.config['db_name']
        db = Database(dbname=dbname)
        return db.table_exists(tablename=self._name)

    def get_model_name(self) -> str:
        if hasattr(self, "_name"):
            tablename: str = getattr(self, "_name")
            tablename = tablename.replace(".", "_")
        else:
            tablename = self.__class__.__name__.lower()
        return tablename

    def generate_model(self):
        fields = inspect.getmembers(self, lambda a: not (inspect.isroutine(a)))
        fields_mysql = []
        for field in fields:
            name, method = field
            action = "get_mysql_field"
            if hasattr(method, action):
                mysql_field = f"{name} {getattr(method, action)()}"
                fields_mysql.append(mysql_field)
            
        query = self.__default_query(fields=fields_mysql)
        print(query)
        return


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
