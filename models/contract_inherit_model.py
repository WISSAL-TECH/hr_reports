from odoo import models, fields, api


class WsContractInherit(models.Model):
    _inherit = 'hr.contract'

    training_title = fields.Char(string="Intitulé de la formation")
    training_start_date = fields.Date(string="Date de début de formation")
    training_end_date = fields.Date(string="Date de fin de formation")
    cart_allowance = fields.Float('Prime de panier')
    transport_allowance = fields.Float('Indemnité de transport')

    cout_hours = fields.Monetary("Cout houres", compute='CalculCoutHours')
    cjm = fields.Monetary('Cjm')
    tjm = fields.Monetary("Tjm")

    salire_net = fields.Monetary("Salaire mensuel(net)")
    salaire_annuel = fields.Monetary("Salaire annuel(brut)")
    salire_monsuel = fields.Monetary("Salaire mensuel(brut)")

    @api.onchange('wage')
    def CalculCoutHours(self):
        for rec in self:
            rec.cout_hours = round(rec.wage / 173.33, 2)