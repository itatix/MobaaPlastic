from odoo import api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError
import base64
import requests
from .vex_soluciones_meli_config import CONDITIONS

class Product(models.Model):
    _name             = 'product.template'
    _inherit          = 'product.template'
    _description      = "Producto de mercado libre"
    id_app            = fields.Char(string="App ID")
    server_meli       = fields.Many2one('meli.synchro.instance', "Instance")
    #is_published      = fields.Boolean(string="Is Published", default=False)
    url_image         = fields.Char(string="url_image")
    product_condition = fields.Selection(CONDITIONS, string='Product Condition', help='Default product condition')
    brand             = fields.Char(string="Product Brand")
    questions_count   = fields.Integer(required=False,compute='_count_questions')
    questions         = fields.One2many('meli.questions','product_id')
    permalink         = fields.Char()
    active_meli       = fields.Boolean(default=True)
    _sql_constraints = [
        ('unique_id_prod_meli','unique(id_app,server_meli)','There can be no duplication of synchronized products')
    ]

    def fun_sync_up(self):
        if not self.image_1920:
            raise ValidationError('THIS PRODUCT DONT HAVE IMAGE')

        return {
                    'name'     : ('Export to ML'),
                    'type'     : 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'meli.export.unite',
                    'target'   : 'new',
                    #'res_id': wiz.id,
                    'context'  : {
                        'default_product': self.id,
                        'default_condition':self.product_condition,
                        'default_brand': self.brand
                    }
                }


    def _count_questions(self):
        for record in self:
            count = self.env['meli.questions'].search_count([('product_id', '=', record.id)])

            if count:
                record.questions_count = count
            else:
                record.questions_count = 0




class Image(models.Model):
    _inherit        = 'product.image'
    id_app          = fields.Char(string="App ID")
    server_meli     = fields.Many2one('meli.synchro.instance', "Server")
    _sql_constraints = [
        ('unique_id_img_meli','unique(id_app,server_meli)','There can be no duplication of synchronized Pictures')
    ]
