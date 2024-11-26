class _Column:
    label: str
    unique: bool
    default: str
    index: bool
    field_type: str
    
    def __repr__(self):
        return f"<{self.__class__.__name__} label={self.label} type={self.field_type}>"


    def parse_kvargs(self, kvargs: dict):
        self.default = kvargs.get("default", None)
        self.unique = bool(kvargs.get("unique", False))
        self.index = bool(kvargs.get("index", False))
        
        if self.default is not None and not isinstance(self.default, (str, int, float)):
            raise ValueError("The 'default' value must be of type str, int, or float.")

    def get_mysql_field(self) -> str:
        field = f"{self.field_type}"

        if self.default is not None:
            if isinstance(self.default, str):
                field += f" DEFAULT '{self.default}'"
            else:
                field += f" DEFAULT {self.default}"

        if self.unique:
            field += " UNIQUE"

        field += f" COMMENT '{self.label}'"
        return field


class Char(_Column):
    size: int
    def __init__(self, label: str, **kvargs) -> None:
        self.parse_kvargs(kvargs=kvargs)
        self.label = label
        self.size = kvargs.get("size", 100)
        self.field_type = f"VARCHAR({self.size})"


class Bool(_Column):
    def __init__(self, label: str, **kvargs) -> None:
        self.parse_kvargs(kvargs=kvargs)
        self.label = label
        self.field_type = "TINYINT(1)"


class Integer(_Column):
    def __init__(self, label: str, **kvargs) -> None:
        self.parse_kvargs(kvargs=kvargs)
        self.label = label
        self.field_type = 'INT'

class BigInteger(_Column):
    def __init__(self, label: str, **kvargs) -> None:
        self.parse_kvargs(kvargs=kvargs)
        self.label = label
        self.field_type = 'BIGINT'

class Float(_Column):
    def __init__(self, label: str, **kvargs) -> None:
        self.parse_kvargs(kvargs=kvargs)
        self.label = label
        self.field_type = 'FLOAT'
        
class DateTime(_Column):
    def __init__(self, label: str, **kvargs) -> None:
        self.parse_kvargs(kvargs=kvargs)
        self.label = label
        self.field_type = "DATETIME"
