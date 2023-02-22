from odoo import models, fields, api

class children(models.Model):
    _name = 'children'

    name = fields.Char(string="Nom", translate=True)
    birthdate = fields.Date(string="Date de naissance")
    parent_id = fields.Many2one('children', 'parent id')

