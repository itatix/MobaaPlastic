from odoo import api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError

class Customers(models.Model):
    _inherit        = 'res.partner'
    _description    = "Clientes de mercado Libre"
    id_app          = fields.Char(string="Meli ID")
    id_customer     = fields.Char(string="Customer ID")
    server_meli     = fields.Many2one('meli.synchro.instance', "Instance Meli")
    id_meli_parent  = fields.Char(string="Meli ID Parent")
    nickname        = fields.Char(string="Customer Nickname")

    _sql_constraints = [
        ('unique_id_clie_meli', 'unique(id_app, server_meli)', 'There can be no duplication of synchronized customers')
    ]