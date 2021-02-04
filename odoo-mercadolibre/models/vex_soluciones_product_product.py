from odoo import api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError

class ProductProduct(models.Model):
    _name                   = 'product.product'
    _inherit                = 'product.product'
    _description            = "Product product de mercado libre"
    id_app_varition         = fields.Char(string="Mercado Libre ID Variation")
    meli_regular_price      = fields.Float()

    _sql_constraints = [
        ('uni_id_variante_prro_meli', 'unique(id_app_varition,server_meli)', 'There can be no duplication of synchronized products Variations')
    ]
    
    @api.depends('list_price', 'price_extra')
    def _compute_product_lst_price(self):
        to_uom = None
        if 'uom' in self._context:
            to_uom = self.env['uom.uom'].browse([self._context['uom']])
        for product in self:
            if to_uom:
                list_price = product.uom_id._compute_price(product.list_price, to_uom)
            else:
                list_price = product.list_price
            api_precio = product.meli_regular_price
            if api_precio:
                product.lst_price = api_precio
            else:
                product.lst_price = list_price + product.price_extra
