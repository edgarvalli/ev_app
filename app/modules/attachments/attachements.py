from app import fields, models
class Attachments(models.Model):
    name = fields.Char('Nombre')
    path = fields.Char('Path')
    