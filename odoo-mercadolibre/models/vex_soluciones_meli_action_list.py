from odoo import api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError
import requests

from .vex_soluciones_meli_config import API_URL

class MeliActionList(models.Model):
    _name               = "meli.action.list"
    _description        = "Meli Action List"
    name                = fields.Char(required = True)
    argument            = fields.Char()
    model               = fields.Char()
    log                 = fields.One2many('meli.logs', 'meli_list')
    interval            = fields.Integer(default=60)
    interval_type       = fields.Selection([('minutes', 'Minutes'), ('hours', 'Hours'),
                                      ('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')], default='minutes')
    active_cron         = fields.Boolean(default=False)
    interval_stock      = fields.Integer(default=60)
    interval_type_stock = fields.Selection([('minutes', 'Minutes'), ('hours', 'Hours'),
                                            ('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')],
                                           default='minutes')
    active_cron_stock = fields.Boolean(default=False)
    automatic           = fields.Boolean()
    ver = fields.Char(compute='_generate_ver')
    total_count         = fields.Integer(compute='_generate_count')
    next_date_cron = fields.Datetime(compute='_generate_next_date', string="Next Execution Date")
    next_date_cron_stock = fields.Datetime(compute='_generate_next_date_stock', string="Next Execution Date")
    export              = fields.Boolean()
    importv             = fields.Boolean()

    def _generate_next_date(self):
        print("aquiii?", self.argument)
        cron = self.env['ir.cron'].search([('argument', '=', str(self.argument)),
                                           "|",
                                           ("active", "=", True), ("active", "=", False)])
        print("croon", cron)
        if cron:
            self.next_date_cron = cron.nextcall
        else:
            self.next_date_cron = None

    def _generate_next_date_stock(self):
        cron = self.env['ir.cron'].search([('argument', '=', 'stock'),
                                           "|",
                                           ("active", "=", True), ("active", "=", False)])
        if cron:
            self.next_date_cron_stock = cron.nextcall
        else:
            self.next_date_cron_stock = None


    def _generate_count(self):
        for record in self:
            model = record.model
            if model:
                count = self.env[str(model)].search_count([('server_meli', '!=', False), ('id_app', '!=', False)])
                record.total_count = count
            else:
                record.total_count = 0

    def write(self, values):
        cron = self.env['ir.cron'].search([('argument', '=', str(self.argument)), "|", ("active", "=", True), ("active", "=", False)])
        if cron:
            interval = values['interval'] if 'interval' in values else self.interval
            interval_type = values['interval_type'] if 'interval_type' in values else self.interval_type
            active = values['active_cron'] if 'active_cron' in values else self.active_cron
            cron.interval_number = interval
            cron.interval_type = interval_type
            cron.active = active

        if self.argument == 'products':
            stock = self.env['ir.cron'].search([('argument', '=', 'stock'),
                                                "|",
                                                ("active", "=", True), ("active", "=", False)])
            if stock:
                active_stock = values['active_cron_stock'] if 'active_cron_stock' in values else self.active_cron_stock
                interval_stock = values['interval_stock'] if 'interval_stock' in values else self.interval_stock
                interval_type_stock = values[
                    'interval_type_stock'] if 'interval_type_stock' in values else self.interval_type_stock
                stock.interval_number = interval_stock
                stock.interval_type = interval_type_stock
                stock.active = active_stock
        res = super(MeliActionList, self).write(values)
        return res

    def sync_products(self):
        print("sync products")
        self.env['meli.action.synchro'].start_sync_products()

    def sync_orders(self):
        print("sync orders")
        self.env['meli.action.synchro'].start_sync_orders()


    def sync_stock(self):
        print("sync stock")
        self.env['meli.stock'].start_update_stock()
