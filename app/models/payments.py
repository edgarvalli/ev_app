from app.tools.evorm import columns, models

class Payments(models.Model):
    _description = 'Tabla de administración de pagos'
    description = columns.Char('Descipción', size=500)
    client_id = columns.Integer('Id Cliente')
    done = columns.Bool('Hecho', default=0)
    payment_date = columns.DateTime('Fecha de Pago')