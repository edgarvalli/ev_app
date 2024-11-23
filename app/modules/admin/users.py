from app import models, fields
class Users(models.Model):
    username: str = fields.Char('Usuaro', 50)
    password: str = fields.Char('Contraseña', 200)
    fullname: str = fields.Char('Nombre', 200)
    
    
    def list(self):
        return True