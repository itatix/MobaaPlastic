from odoo import api, fields, models
import threading
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from ..models.vex_soluciones_meli_config  import API_URL
import requests

class Inventory(models.Model):
    _inherit     = 'stock.inventory'
    stock_meli    = fields.Boolean(default=False)

class MeliStock(models.TransientModel):
    _name               = "meli.stock"
    _description        = "Synchronized  MercadoLibre Stock"
    server_meli         = fields.Many2one('meli.synchro.instance', "Instance", required=True)

    def update_stock(self, server):
        location = server.warehouse.lot_stock_id
        company  = server.company
        print("aquiii 1")
        if not location:
            raise ValidationError('Set Up warehouse')
        if not company:
            raise ValidationError('Set Up Company')

        print("aquiii 2")
        
        products = self.env['product.template'].search([('server_meli', '=', server.id)])
        for product in products:
            id_app = product.id_app
            #print("aquiii 3", product.name, id_app)
            if id_app:
                variants = self.env['product.product'].search([('product_tmpl_id','=',product.id)])
                count = self.env['product.product'].search_count([('product_tmpl_id','=',product.id)])
                json_stock = {
                    'name': 'Inv Meli: ' + str(product.name),
                    'prefill_counted_quantity': 'counted',
                    'location_ids': [(6, 0,[location.id ])] ,
                    'stock_meli': True,
                    'company_id': company.id,
                }

                #crear el inventario
                inventory = self.env['stock.inventory'].create(json_stock)
                if count > 0:
                    for variant in variants:
                        inventory.product_ids += variant
                        '''
                        if variant.id_app_varition:
                            inventory.product_ids += self.env['product.product'].search([('id', '=', int(variant.id))])
                        else:
                            inventory.product_ids += self.env['product.product'].search([('product_tmpl_id', '=', int(product.id))])
                        '''


                    inventory.action_start()
                    product_product_ids = []
                    inventory_line = self.env['stock.inventory.line']

                    for variante in variants:
                        variante.write({'type':'product'})
                        if variante.id_app_varition:
                            #consultar la info de la variante
                            variante_url = '{}/items/{}/variations/{}'.format(API_URL,str(id_app),str(variante.id_app_varition))
                            res = requests.get(variante_url)
                            variant_meli = res.json()
                            variant_meli_id = variant_meli['id']
                            variant_meli_quantity = variant_meli['available_quantity']
                            variant_odoo = self.env['product.product'].search([('id_app_varition', '=', variant_meli_id),
                                                                               ('product_tmpl_id', '=', product.id)])
                            if variant_odoo:
                                variant_inventory = inventory_line.search([('product_id','=',variant_odoo.id),
                                                                           ('inventory_id','=',inventory.id)])
                                if variant_inventory:
                                    variant_inventory.write({
                                        'product_qty': int(variant_meli_quantity)
                                    })
                                else:
                                    variant_inventory = self.env['stock.inventory.line'].create({
                                        'product_id': variant_odoo.id,
                                        'product_qty': variant_meli_quantity,
                                        'location_id': inventory.location_ids[0].id,
                                        'inventory_id': inventory.id,
                                        'product_uom_id': variant_odoo.uom_id.id,
                                        'company_id': company.id,
                                    })
                        else:
                            #obtener solo del producto
                            product_url = '{}/items/{}'.format(API_URL,str(id_app))
                            res = requests.get(product_url)
                            res = res.json()
                            quantity = res['available_quantity']
                            variant_odoo = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])
                            if variant_odoo:
                                variant_inventory = inventory_line.search([('product_id','=',variant_odoo.id),('inventory_id','=',inventory.id)])
                                if variant_inventory:
                                    variant_inventory.write({
                                        'product_qty': int(quantity)
                                    })
                                else:
                                    variant_inventory = self.env['stock.inventory.line'].create({
                                        'product_id': variant_odoo.id,
                                        'product_qty': int(quantity),
                                        'location_id': inventory.location_ids[0].id,
                                        'inventory_id': inventory.id,
                                        'product_uom_id': variant_odoo.uom_id.id,
                                        'company_id': company.id,
                                    })


                inventory.action_validate()
                            
            else:
                print("No existe ID APP en el producto, ", product.name)

            
    def meli_update_stock(self):
        server = self.server_meli
        print('\n\n\n server_meli', server)
        # accion = self.accion
        threaded_synchronization = threading.Thread(target=self.update_stock(server))
        threaded_synchronization.run()

    def start_update_stock(self):
        accion = self.env['meli.action.list'].search([('argument', '=', 'products')])
        # obtener todos los servidores
        servers = self.env['meli.synchro.instance'].search([('active_automatic', '=', True)])
        for server in servers:
            start_date = fields.Datetime.now()
            threaded_synchronization = threading.Thread(target=self.update_stock(server))
            threaded_synchronization.run()
            end_date = fields.Datetime.now()
            accion.log += self.env['meli.logs'].new({
                'start_date'  : start_date,
                'end_date'    : end_date,
                'description' : 'Update Stock',
                'state'       : 'done'
            })
