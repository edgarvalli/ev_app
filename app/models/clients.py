from app.tools.evschema import columns, models

class Customers(models.Model):
    name = columns.Char('Nombre', size=200)
    email = columns.Char('Correo', size=200, index=True, unique=True)
    rfc = columns.Char('RFC', size=15, index=True, unique=True)
    company_name = columns.Char('Empresa', size=200)
    active = columns.Bool('Activo')