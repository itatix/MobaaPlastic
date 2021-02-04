from odoo import api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError

class Categories(models.Model):
    _name                   = 'product.public.category'
    _inherit                = 'product.public.category'
    _description            = "Categorias de mercado libre"
    id_app                  = fields.Char(string="App ID" ,default =  None)
    server_meli             = fields.Many2one('meli.synchro.instance', "Instance Meli")
    _sql_constraints = [
        ('unique_id_cat_meli', 'unique(id_app, server_meli)', 'There can be no duplication of synchronized categories')
    ]