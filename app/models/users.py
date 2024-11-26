from app.tools.evorm import columns, models

class Users(models.Model):
    username = columns.Char('Usuario', size=50)
    email = columns.Char('Correo', unique=True, index=True)
    password = columns.Char('Password', size=200)
    fullname = columns.Char('Nombre', size=200)
    is_admin = columns.Bool('Administrador')