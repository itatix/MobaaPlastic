from odoo import api, fields, models

class Orders(models.Model):
    _inherit                = 'sale.order'
    _description            = "Ordenes de mercado libre"

    id_app                  = fields.Char(string="Product ID")
    server_meli             = fields.Many2one('meli.synchro.instance', "Instance")
    meli_order_id           = fields.Char(string='Meli Order Id',index=True)
    #meli_orders             = fields.Many2many('mercadolibre.orders',string="ML Orders")
    meli_status             = fields.Selection( [
        #Initial state of an order, and it has no payment yet.
                                        ("confirmed","Confirmado"),
        #The order needs a payment to become confirmed and show users information.
                                      ("payment_required","Pago requerido"),
        #There is a payment related with the order, but it has not accredited yet
                                    ("payment_in_process","Pago en proceso"),
        #The order has a related payment and it has been accredited.
                                    ("paid","Pagado"),
        #The order has not completed by some reason.
                                    ("cancelled","Cancelado")], string='Order Status');

    meli_status_detail      = fields.Text(string='Status detail, in case the order was cancelled.')
    meli_date_created       = fields.Datetime('Creation date')
    meli_date_closed        = fields.Datetime('Closing date')

#        'meli_order_items': fields.one2many('mercadolibre.order_items','order_id','Order Items' ),
#        'meli_payments': fields.one2many('mercadolibre.payments','order_id','Payments' ),
    meli_shipping           = fields.Text(string="Shipping")

    meli_total_amount       = fields.Float(string='Total amount')
    meli_shipping_cost      = fields.Float(string='Shipping Cost',help='Gastos de envío')
    meli_shipping_list_cost = fields.Float(string='Shipping List Cost',help='Gastos de envío, costo de lista/interno')
    meli_paid_amount        = fields.Float(string='Paid amount',help='Paid amount (include shipping cost)')
    meli_fee_amount         = fields.Float(string='Fee amount',help="Comisión")
    meli_currency_id        = fields.Char(string='Currency ML')
#        'buyer': fields.many2one( "mercadolibre.buyers","Buyer"),
#       'meli_seller': fields.text( string='Seller' ),
    meli_shipping_id        =  fields.Char('Meli Shipping Id')
    #meli_shipment           = fields.Many2one('mercadolibre.shipment',string='Meli Shipment Obj')
    
    _sql_constraints = [
        ('unique_id_order_meli', 'unique(id_app, server_meli)', 'There can be no duplication of synchronized Orders')
    ]