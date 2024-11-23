class Char:
    label: str
    size: int
    
    
    def __init__(self, label: str, size: int = 100) -> None:
        self.label = label
        self.size = size
    
    def get_mysql_field(self) -> str:
        field = f'varchar({self.size})'
        return field