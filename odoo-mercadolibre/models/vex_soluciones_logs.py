from odoo import api, fields, models

class Logs(models.Model):
    _name           = "meli.logs"
    meli_list       = fields.Many2one('meli.action.list')
    server          = fields.Many2one('meli.synchro.instance')
    start_date      = fields.Datetime()
    end_date        = fields.Datetime()
    state           = fields.Selection([('error', 'Error'),('done', 'Done')])
    description     = fields.Char()
    
