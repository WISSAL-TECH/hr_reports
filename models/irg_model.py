from odoo import models, fields, api


class BaremeIrg(models.Model):
    _name = 'bareme.irg'
    _description = 'irg'

    irg_salaire_imposable = fields.Integer(string="Salaire imposable")
    irg_regime_general = fields.Integer(string="IRG régime géneral")
    irg_cas_particulier= fields.Integer(string="IRG cas particulier")

