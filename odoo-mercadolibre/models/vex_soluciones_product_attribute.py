from odoo import api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError

class Attributes(models.Model):
    _inherit            = 'product.attribute'
    _description        = "Atributos de mercado libre"
    id_app              = fields.Char(string="Meli ID")
    id_product          = fields.Char(string="Product ID")
    server_meli         = fields.Many2one('meli.synchro.instance', "Instance")

    _sql_constraints = [
        ('unique_id_atrr_meli', 'unique(id_app, server_meli)', 'There can be no duplication of synchronized Attribute')
    ]

class TerminosAtributos(models.Model):
    _inherit            = 'product.attribute.value'
    id_app              = fields.Char(string="Meli ID")
    server_meli         = fields.Many2one('meli.synchro.instance', "Server")
