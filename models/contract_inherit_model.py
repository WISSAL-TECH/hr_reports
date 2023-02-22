from odoo import models, fields, api


class WsContractInherit(models.Model):
    _inherit = 'hr.contract'

    training_title = fields.Char(string="Intitulé de la formation")
    training_start_date = fields.Date(string="Date de début de formation")
    training_end_date = fields.Date(string="Date de fin de formation")
