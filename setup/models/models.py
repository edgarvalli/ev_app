from app.tools.evschema import columns, models

class Models(models.Model):
    
    name = columns.Char('Modelo', size=300, unique=True)
    description = columns.Char('Descripción', size=500)
    active = columns.Bool('Activo')