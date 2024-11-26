from app.tools.evorm import columns, models

class Config(models.Model):
    name = columns.Char('Nombre', size=50,index=True, unique=True)
    value = columns.Char('Correo', size=200)
    active = columns.Bool('Activo')