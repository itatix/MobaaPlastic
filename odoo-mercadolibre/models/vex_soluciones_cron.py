from odoo import api, fields, models
class VexCron(models.Model):
    _inherit = 'ir.cron'
    argument   = fields.Char()
    _sql_constraints = [
        ('unique_id_cron_meli_vex', 'unique(argument)', 'There can be no duplication of synchronized Argument')
    ]
