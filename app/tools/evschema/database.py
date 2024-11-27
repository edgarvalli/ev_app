import csv
import pymysql
from pathlib import Path
import pymysql.cursors


def build_condition(key: str, cond: str, param: str | int, operator: str = None) -> str:
    if cond == "like":
        param = param.replace("*", "%")  # Usar % en lugar de *

    # Convertir números a cadenas de texto de forma adecuada
    if isinstance(param, str) and not param.isdigit():
        param = f"'{param}'"

    operator_str = ""
    if operator is not None:
        if operator == "|":
            operator_str = " OR "
        else:
            operator_str = " AND "
    return f"{operator_str}{key} {cond} {param}"

class DBConfig:
    dbhost: str
    dbport: int
    dbuser: str
    dbpass: str
    dbname: str
    dbprefix: str

    def __init__(self) -> None:
        self.dbhost = "localhost"
        self.dbport = 3306
        self.dbuser = "root"
        self.dbpass = "p4ssw0rd"
        self.dbname = "mysql"
        self.dbprefix = ""

    def parse_from_dict(self, config: dict):
        for key in config.keys():
            if hasattr(self, key):
                setattr(self, key, config[key])

class Database:

    mysql_connection: pymysql.Connection
    mysql_cursor = pymysql.cursors.Cursor
    config: DBConfig = None

    def __init__(self) -> None:
        self.config = DBConfig()
        self.mysql_connection = None
        self.mysql_cursor = None

    def connect(self):
        if self.mysql_connection is None or not self.mysql_connection.open:
            try:
                self.mysql_connection = pymysql.connect(
                    host=self.config.dbhost,
                    port=self.config.dbport,
                    user=self.config.dbuser,
                    password=self.config.dbpass,
                    database=self.config.dbname,
                )

                self.mysql_cursor = self.mysql_connection.cursor(pymysql.cursors.DictCursor)
            except pymysql.ProgrammingError as e:
                print("Ocurrio un error al conectar con la base de datos: " + e)

    def database_exists(self, dbname) -> bool:
        exists = True

        query = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{dbname}';"

        dbexists = self.query(query=query).fetchone()
        if dbexists is None:
            exists = False
        return exists

    def new_database(self, dbname):
        self.config.dbname = "mysql"
        self.connect()
        query = f"CREATE DATABASE IF NOT EXISTS {dbname}"
        self.mysql_cursor.execute(query)
        self.mysql_connection.commit()
        self.changedb(dbname=dbname)
        self.config.dbname = dbname

    def table_exists(self, tablename) -> bool:
        exists = False
        self.connect()
        alias = "table_exists"
        query = f"""
            SELECT COUNT(*) AS {alias}
            FROM information_schema.tables 
            WHERE table_schema = '{self.config.dbname}' 
            AND table_name = '{tablename}';
        """

        exc = self.query(query=query)

        result = exc.fetchone()

        if result[alias] > 0:
            exists = True

        return exists

    def close(self):
        try:
            if self.mysql_connection.open:
                self.mysql_connection.close()
        except pymysql.InternalError as e:
            print(e.msg)

    def changedb(self, dbname: str):
        self.dbname = dbname
        self.mysql_connection.select_db(dbname)

    def search(self, model: str, **kvargs):
        response = {"error": True, "message": "", "columns": {}, "data": []}

        fields = kvargs.get("fields", "*")
        where = kvargs.get("where", None)
        limit = kvargs.get("limit", "50")
        query = f"SELECT {fields} FROM {model}"

        if where:

            conditions = []

            if is_bidimensional(where):
                for i, condition in enumerate(where):

                    if len(condition) == 3:
                        a, b, c = condition
                        condition = (a, b, c, "&")
                    key, cond, param, operator = condition
                    if i == 0:
                        conditions.append(
                            build_condition(key=key, cond=cond, param=param)
                        )
                    else:
                        conditions.append(
                            build_condition(
                                key=key, cond=cond, param=param, operator=operator
                            )
                        )
            else:
                if len(where) == 3:
                    a, b, c = where
                    condition = (a, b, c, "&")

                key, cond, param, operator = condition
                conditions.append(build_condition(key=key, cond=cond, param=param))

            query += f" WHERE {''.join(conditions)}"

        query += " ORDER BY id DESC LIMIT " + limit + ";"

        columns = self.get_description_model(model=model)

        if fields != "*":
            fields = fields.split(",")
            response["columns"] = [obj for obj in columns if obj["name"] in fields]
        else:
            response["columns"] = columns
            
        
        def set_error_response(msg: str):
            response["error"] = False
            response["message"] = msg

        # try:
        #     response["data"] = self.query(query=query).fetchall()
        #     response["error"] = False
        #     response["message"] = query
        # except pymysql.ProgrammingError as e:
        #     set_error_response(e)
        # except pymysql.DatabaseError as e:
        #     set_error_response(e)
        # except pymysql.DataError as e:
        #     set_error_response(e)
        # except pymysql.Error as e:
        #     set_error_response(e)
        # except pymysql.MySQLError as e:
        #     set_error_response(e)
        # except pymysql.ProgrammingError as e:
        #     set_error_response(e)
        # except:
        #     set_error_response("Ocurrio un error al procesar la petición")

        response["data"] = self.query(query=query).fetchall()
        response["error"] = False
        response["message"] = query
        return response

    def query(self, query: str) -> pymysql.cursors.DictCursor:
        if self.mysql_connection is None or not self.mysql_connection.open:
            self.connect()
        self.mysql_cursor.execute(query)
        return self.mysql_cursor

    def save(self, model: str, record: dict) -> dict:

        fields = record.keys()
        values = record.values()
        values_key = [f"%s" for _ in values]
        query = f"INSERT INTO {model} ({','.join(fields)}) VALUES ({values_key})"

        try:
            self.mysql_cursor.execute(query, record)
            self.mysql_connection.commit()
        except pymysql.IntegrityError as e:
            return {"error": True, "message": e.msg}

        self.close()
        return {"error": False, "message": f"Records inserted;"}

    def update(self, model: str, id: int, data: dict) -> dict:
        params = []

        for k, v in data.items():  # Cambiamos a data.items()
            if not isinstance(v, (int, float)):  # Verifica si no es número
                v = f"'{v}'"  # Asegura que las cadenas estén entre comillas simples

            params.append(f"{k}={v}")

        query = f"UPDATE {model} SET {', '.join(params)} WHERE id={id}"

        try:
            self.connect()
            self.mysql_cursor.execute(query)
            self.mysql_connection.commit()
        except pymysql.IntegrityError as e:
            return {"error": True, "message": e.msg}
        finally:
            self.close()

        return {
            "error": False,
            "message": f"Record with id {id} was updated",
            "data": id,
        }

    def unlink(self, model: str, id: int) -> dict:
        query = f"DELETE FROM {model} WHERE id={id}"
        try:
            self.connect()
            self.mysql_cursor.execute(query)
            self.mysql_connection.commit()
        except pymysql.IntegrityError as e:
            return {"error": True, "message": e.msg}
        finally:
            self.close()

        return {
            "error": False,
            "message": f"Record with id {id} was removed",
            "data": id,
        }

    def bulk_from_csv(self, csv_path: str) -> dict:
        csv_path: Path = Path(csv_path)
        response = {"error": True, "message": ""}
        if not csv_path.exists():
            response["message"] = "Path no exists!!!!"
            return response

        if not csv_path.name.endswith(".csv"):
            response["message"] = "Is not a csv valid!!!!"
            return response

        model = csv_path.name[:-4]

        with open(csv_path, mode="r", newline="", encoding="utf-8") as csv_file:

            records = [tuple(row) for row in csv.reader(csv_file)]
            self.bulk(model, records)

    def bulk(self, model: str, records: list[dict] | list[tuple]) -> dict:
        if not records:
            return {"error": True, "message": "The list is empty"}

        if isinstance(records[0], dict):
            fields = records[0].keys()
            values = [tuple(record.values()) for record in records]
        else:
            fields = records[0]  # Los campos ya están definidos
            values = records[1:]

        values_key = ["%s"] * len(fields)

        # Creamos el query
        query = f"INSERT IGNORE INTO {model} ({','.join(fields)}) VALUES ({','.join(values_key)})"

        try:
            self.connect()
            self.mysql_cursor.executemany(query, values)
            self.mysql_connection.commit()
        except pymysql.IntegrityError as e:
            return {"error": True, "message": e.msg}
        finally:
            self.close()

        return {"error": False, "message": f"Records inserted; Total: {len(records)}"}

    def get_description_model(self, model: str) -> list[dict]:
        query = """
        SELECT COLUMN_NAME name, COLUMN_COMMENT comment, COLUMN_TYPE type
        FROM information_schema.COLUMNS
        WHERE TABLE_NAME = %s AND TABLE_SCHEMA = %s;
        """

        self.connect()
        self.mysql_cursor.execute(query, (model, self.config.dbname))

        columns = self.mysql_cursor.fetchall()

        return columns
