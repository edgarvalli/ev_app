import json, hashlib
import mysql.connector as mysql_connect
from os import path


root_path = path.dirname(__file__)
root_path = path.abspath(path.join(root_path, ".."))
file_config = open(path.join(root_path, "config.json"), "r")
config_json = file_config.read()
file_config.close()
config: dict = json.loads(config_json)
dbname = f"{config['db_prefix']}_main"


def create_table_query(tablename: str, fields: tuple) -> str:
    query = f"CREATE TABLE IF NOT EXISTS {dbname}.{tablename} (id int primary key auto_increment,{','.join(fields)},create_date datetime default current_timestamp,update_date datetime default current_timestamp)"
    return query


querys = [
    f"CREATE DATABASE IF NOT EXISTS {dbname};",
    create_table_query(
        "users",
        (
            "username varchar(100) unique",
            "password varchar(200)",
            "fullname varchar(200)",
            "email varchar(100)",
            "phone varchar(20)",
            "is_admin tinyint",
            "active tinyint",
            "last_login datetime",
        ),
    ),
    create_table_query(
        "companys",
        (
            "name varchar(200)",
            "rfc varchar(15)",
            "address varchar(200)",
            "zip int",
            "city varchar(50)",
            "state varchar(50)",
            "country varchar(50)",
            "users_id int",
            "users_fullname varchar(200)",
        ),
    ),
    create_table_query(
        "menu", ("label varchar(50)", "link varchar(100)", "icon varchar(20)")
    ),
    create_table_query(
        "plans",
        (
            "name varchar(50)",
            "description varchar(200)",
            "price float",
            "active tinyint",
        ),
    ),
]


conn = mysql_connect.connect(
    host=config.get("db_host", "localhost"),
    port=config.get("db_port", 3306),
    user=config.get("db_user", "sag"),
    password=config.get("db_pass", "sagpwf"),
    database="mysql",
)

cur = conn.cursor(dictionary=True)

for query in querys:
    cur.execute(query)
    conn.commit()

conn.database = dbname
query = f"SELECT id FROM users WHERE username='admin' LIMIT 1"

cur.execute(query)
exists = cur.fetchone()

if exists is None:
    users = [
        (
            "admin",
            hashlib.sha1(b"admin").hexdigest(),
            "Administrador",
            "edgarvalli80@gmail.com",
            "8121476458",
            1,
            1
        )
    ]

    cur.executemany(
        "INSERT INTO users (username,password,fullname,email,phone,is_admin,active) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        users,
    )
    conn.commit()

rfc: str = config.get('prefix','sag')
query = f"SELECT id FROM companys WHERE rfc='{rfc.upper()}' LIMIT 1"
cur.execute(query)
exists = cur.fetchone()

if exists is None:
    query = "SELECT id, fullname FROM users WHERE username='admin'"
    cur.execute(query)
    user = cur.fetchone()
    companys = [
        (
            "Sistema de Administración General",
            rfc.upper(),
            user.get('id',1),
            user.get('fullname', 'Administrador')
        )
    ]
    
    cur.executemany("INSERT INTO companys (name,rfc,users_id,users_fullname) VALUES (%s,%s,%s,%s)", companys)
    conn.commit()
    
cur.close()
conn.close()
