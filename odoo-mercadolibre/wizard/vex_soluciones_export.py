from odoo import api, fields, models
import threading
import requests
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from odoo.addons.payment.models.payment_acquirer import ValidationError
from ..sdk.meli.configuration import  Configuration
from ..sdk.meli.api_client import ApiClient
from ..sdk.meli.api import RestClientApi
import base64
from ..models.vex_soluciones_meli_config import API_URL
from ..models.vex_soluciones_meli_config import CONDITIONS

class MeliMultiExport(models.TransientModel):
    _name = "meli.export"
    server = fields.Many2one('meli.synchro.instance',
                             "Instance", required=True)
    action = fields.Many2one('meli.action.list')
    model = fields.Char(related="action.model")
    products = fields.Many2many('product.template')

    def export_product(self,p,server,self2):
        if not p.image_1920:
            raise ValidationError('THIS PRODUCT DONT HAVE IMAGE')
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        foto_main = base_url+"/web/image?model=product.template&id={}&field=image_128&unique=".format(p.id)

        headers = { "Content-Type": "application/json"}
        #url = self.env['shop.action.synchro'].shop_url(self.server, str(argument))
        url = 'https://api.mercadolibre.com/items?access_token='+str(server.access_token)
        cc = self2.category_children if  self2.category_children else self2.category
        #raise ValidationError(cc.id_app)
        data = {
               "site_id":str(server.meli_country),
               "title":str(p.name),
               "category_id":str(cc.id_app),
               "price":float(p.list_price),
               "currency_id":str(server.default_currency),
               "buying_mode":str(self2.buying_mode),
               "listing_type_id":str(self2.listing_type_id),
               "condition":str(self2.condition),
               "available_quantity":int(self2.quantity),
               "pictures": [
                       { "source": foto_main}
               ],
       }

        r = requests.post(url, json=data, headers=headers)
        data = r.json()
        if 'id' in data:
             p.write({
                        'server_meli': server.id,
                        'id_app': data['id'],
                            })
        else:
            import json
            raise ValidationError(json.dumps(data))
            #raise ValidationError('AN ERROR HAS OCCURRED, TRY AGAIN')


    def export_export(self):
        threaded_synchronization = threading.Thread(target=self.start_export())
        threaded_synchronization.run()


    def start_export(self):
        model = self.model
        access_token = self.server.access_token
        if 1  == 1:
            if model == 'product.template':
                products = self.products
                for product in products:
                    self.export_product(product,self.server,self.category)

class MeliUnitExport(models.TransientModel):
    _name              = "meli.export.unite"
    server             = fields.Many2one('meli.synchro.instance',"Instance", required=True)
    product            = fields.Many2one('product.template',required=True)
    category           = fields.Many2one('product.public.category',required=True)
    category_children  = fields.Many2one('product.public.category')
    brand              = fields.Char()
    condition          = fields.Selection(CONDITIONS, string='Product Condition', required=True)
    quantity           = fields.Integer(required=True,default=10)
    buying_mode        = fields.Selection([('buy_it_now','buy it now'),('classified','classified')], required=True)
    listing_type_id    = fields.Selection([('free','free'),('bronze','bronze'),('gold_special','gold special')], required=True)


    def start_export(self):
        self.env['meli.action.synchro'].check_synchronize(self.server)
        self.env['meli.export'].export_product(self.product,self.server,self)

    def predict_category(self):
        predict_url = '{}/sites/{}/category_predictor/predict'.format(API_URL, self.server.meli_country)
        payload = {'title': self.product.name}
        res = requests.get(predict_url, params=payload)
        if res.status_code == 200:
            res = res.json()
            cat_id = res['id']
            cc = self.env['product.public.category'].search([('id_app','=',cat_id)])
            if cc:
                self.category_children=cc.id
                self.category=cc.id

    @api.onchange('server')
    def check_category(self):
        self.env['meli.action.synchro'].check_synchronize(self.server)
        self.predict_category()
    @api.onchange('category_children')
    def set_category_padre(self):
        self.category = self.category_children
    @api.onchange('category')
    def set_childrens(self):
        self.env['meli.action.synchro'].insert_categorias_children(str(self.category.id_app),self.server,self.category)
















