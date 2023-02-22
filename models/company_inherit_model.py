from odoo import models, fields, api

class WsCompanyInherit(models.Model):
    _inherit = 'res.company'

    manager_id = fields.Many2one('hr.employee', string="Manager")
    registration_number = fields.Char(string="Numéro d'enregistrement")
    membership_number = fields.Char(string="Numéro d'adhésion")

