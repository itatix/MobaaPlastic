# -*- coding: utf-8 -*-
# from odoo import http


# class Odoo-mercadolibre(http.Controller):
#     @http.route('/odoo-mercadolibre/odoo-mercadolibre/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo-mercadolibre/odoo-mercadolibre/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo-mercadolibre.listing', {
#             'root': '/odoo-mercadolibre/odoo-mercadolibre',
#             'objects': http.request.env['odoo-mercadolibre.odoo-mercadolibre'].search([]),
#         })

#     @http.route('/odoo-mercadolibre/odoo-mercadolibre/objects/<model("odoo-mercadolibre.odoo-mercadolibre"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo-mercadolibre.object', {
#             'object': obj
#         })
