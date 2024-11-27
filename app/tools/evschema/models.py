import inspect
from .database import Database, DBConfig


class Model:
    _name: str
    _description: str
    config: DBConfig
    index: list
    
    def __init__(self, app = None) -> None:
        self.app = app
        self._name = self.get_model_name()
        self.index = []

    def __run_build(self):
        if not self.check_is_model_exists():
            self.generate_model()

    def build(self, config: DBConfig) -> None:
        self.config = config
        if self.app is None:
            self.__run_build()
        else:
            with self.app.app_context():
                self.__run_build()
    
    def get_index_definitions(self) -> list[str]:
        definitions = []
        for name, unique in self.index:
            index_type = "UNIQUE " if unique else ""
            definitions.append(f"{index_type}INDEX idx_{self._name}_{name} ({name})")
        return definitions

    def __default_query(self, fields: list[str]) -> str:
        all_fields = ["id INT AUTO_INCREMENT PRIMARY KEY"]
        all_fields.extend(fields)
        all_fields.append("create_date DATETIME DEFAULT CURRENT_TIMESTAMP")
        all_fields.append(
            "update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        )
        
        all_fields.extend(self.get_index_definitions())
        
        query = f"CREATE TABLE IF NOT EXISTS {self.config.dbname}.{self._name} ({','.join(all_fields)})"
        return query

    def check_is_model_exists(self):
        try:
            db = Database()
            return db.table_exists(tablename=self._name)
        except Exception as e:
            print(f"Error checking if table exists: {e}")
            return False

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
                unique = getattr(method, 'unique')
                mysql_field = f"{name} {getattr(method, action)()}"
                
                if getattr(method, 'index'):
                    self.index.append((name, unique))
                    if unique:
                        mysql_field = mysql_field.replace('UNIQUE', '')                
                
                fields_mysql.append(mysql_field)

        query = self.__default_query(fields=fields_mysql)
        
        print(query)
        
        print("===================================================================")
        
        print(f'Creating table {self._name} on database {self.config.dbname}.....')
        
        db = Database()
        db.config = self.config
        db.query(query=query)
        db.mysql_connection.commit()
        
        return
