import mysql.connector
from flask import current_app
import mysql.connector.abstracts

class Database:
    
    dbname: str
    mysql_connection: mysql.connector.MySQLConnection
    mysql_cursor = mysql.connector.abstracts.MySQLCursorAbstract
    
    def __init__(self, dbname: str = None) -> None:
        
        if dbname is None:
            self.dbname = current_app.config.get('db_name', 'sag')
        else:
            self.dbname = dbname
        self.mysql_connection = None
        self.mysql_cursor = None
    
    def connect(self):
        if self.mysql_connection is None or not self.mysql_connection.is_connected():
            self.mysql_connection = mysql.connector.connect(
                host = current_app.config.get('db_host', 'localhost'),
                port = current_app.config.get('db_port', 3306),
                user = current_app.config.get('db_user', 'sag'),
                password = current_app.config.get('db_pass', 'sagpwf'),
                database = self.dbname
            )
            
            self.mysql_cursor = self.mysql_connection.cursor(dictionary=True)
    
    def table_exists(self, tablename) -> bool:
        exists = False
        self.connect()
        alias = 'table_exists'
        query = f"""
            SELECT COUNT(*) AS {alias}
            FROM information_schema.tables 
            WHERE table_schema = '{self.dbname}' 
            AND table_name = '{tablename}';
        """
        
        exc = self.query(query=query)
        
        result = exc.fetchone()
        
        if result[alias] > 0:
            exists = True
        
        return exists
    
    def close(self):
        if self.mysql_connection.is_connected():
            self.mysql_connection.close()
    
    def changedb(self, dbname: str):
        self.dbname = dbname
        self.mysql_connection.database = dbname
    
    def query(self, query: str) -> mysql.connector.abstracts.MySQLCursorAbstract:
        self.connect()
        self.mysql_cursor.execute(query)
        return self.mysql_cursor
    
    def fetchall(self, model: str, fields: str = '*', where: str = None,limit: int = 50 ) -> list[dict]:
        
        if where is not None:
            query = f"SELECT {fields} FROM {model} WHERE {where} ORDER BY id DESC LIMIT {limit}"
        else:
            query = f"SELECT {fields} FROM {model} ORDER BY id DESC LIMIT {limit}"
        
        self.connect()
        
        self.mysql_cursor.execute(query)
        rows = self.mysql_cursor.fetchall()
        
        self.close()
        
        return rows