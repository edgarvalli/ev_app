from app.tools.evorm import columns, models

class Plans(models.Model):
    
    name = columns.Char('Modelo', size=300)
    description = columns.Char('Etiqueta', size=500)
    active = columns.Bool('Activo')
    
class PermissionsPlans(models.Model):
    _name = 'perm_plans'
    
    customers_id = columns.Integer('Id Cliente')
    plans_id =columns.Integer('Id Plan')
    models_id = columns.Integer('Id Modelo')
    prem_read = columns.Bool('Lectura')
    prem_write = columns.Bool('Escritura')
    prem_delete = columns.Bool('Eliminar')