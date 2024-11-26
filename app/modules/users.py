from app.api import HttpAPIResponse


class users:
    
    def __init__(self):
        self.response = HttpAPIResponse()
    
    def search(self, data: dict):
        return self.response.todict()