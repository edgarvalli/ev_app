from app.tools.evorm import columns, models

class Menu(models.Model):
    
    link = columns.Char('Link', size=300, unique=True, null=True)
    label = columns.Char('Etiqueta')
    active = columns.Bool('Activo')