class Char:
    size: int
    def __init__(self, size) -> None:
        self.size = size
    
    def get_mysql_field(self):
        return 'varchar(' + self.size + ')'