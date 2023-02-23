from odoo import models, fields, api


class hr_report(models.Model):
    _inherit = 'hr.employee'

    is_trainee = fields.Selection([('stagiaire', 'Stagiaire'), ('employee', 'Employé')], default="employee", string="Type", translate=True)
    date_start_training = fields.Date(string="Date de début de stage", invisible=True)
    date_end_training = fields.Date(string="Date de fin de stage", invisible=True)
    training_duration = fields.Integer(string="Pèriode de stage", invisible=True)
    job_description = fields.Char(string="Description du poste", translate=True)
    job_principal_mission = fields.Text(string="Missions pincipales du poste", translate=True)
    job_secondary_mission = fields.Text(string="Missions secondaires du poste", translate=True)
    job_tasks = fields.Text(string="Tâches", translate=True)
    job_finality = fields.Text(string="Finalités du poste", translate=True)
    socio_pro_category = fields.Selection([('executant', 'Exécutant'), ('maitrise', 'Maitrise'), ('cadre', 'Cadre'),
                                            ('Cadre_dirigeant', 'Cadre Dirigeant')], string="Catégorie Socio-pro",
                                           translate=True)
    father_name = fields.Char(string="Nom du père", translate=True)
    mother_name = fields.Char(string="Nom de la mère", translate=True)
    date_reprise = fields.Date(string="Date de reprise du travail")
    children_names = fields.One2many('children', 'id', string="Noms des enfants")

    work_mode = fields.Selection([('Télétravail', 'télétravail'), ('Présentiel', 'présentiel')],
                                    string="Mode de travail", default="Présentiel")
    experience_years = fields.Integer(string="Années d'expérience")

    document_type = fields.Selection(
        [('Carte Nationale', 'carte nationnale'), ('permis de conduire', 'Permis de conduire')],
        string="Type de pièce d'identité", default="Carte Nationale")

    date_start_trial = fields.Date(string="Date de début d\'essai")
    date_end_trial = fields.Date(string="Date de fin d\'essai")

    prolongation = fields.Boolean(string="Prolongation")
    prolongation_duration = fields.Date(string="Durée de prolongation")
    date_start_prolongation = fields.Date(string="Date de début de prolongation")
    date_end_prolongation = fields.Date(string="Date de fin de prolongation")

    social_advantages = fields.Boolean(string="Avantages sociaux")
    social_security_number = fields.Char(string="N° de sécurité sociale")
    contributions_nature = fields.Selection(
        [('Régime général', 'R22: Régime général'), ('R06: Abattement de 40%', 'R06: Abattement de 40%'),
         ('R07: Abattement de 80%', 'R07: Abattement de 80%'), ('R08: Abattement de 90%', 'R08: Abattement de 90%')],
        string="Nature des cotisations")
    abatement_decision_number = fields.Integer(string="N° d'abattement")
    date_start_abatement = fields.Date(string="Début de l\'abattement")
    date_end_abatement = fields.Date(string="Fin de l\'abattement")

    no_active_employee = fields.Boolean(string="Non actif")
    departure_date = fields.Date(string="Date de départ")
    departure_reason = fields.Text(string="Raison de départ")

    equipment_owner = fields.Selection([('Entreprise', 'entreprise'), ('Personnel', 'personnel')],
                                               string="Propriétaire de l'équipement", default="Entreprise")
    pc = fields.Boolean(string="PC")
    pc_grant_date = fields.Date(string="Date d'attribution")
    pc_characteristics = fields.Text(string="Caractéristiques")

    peripheral = fields.Boolean(string="Périphérique")
    peripheral_grant_date = fields.Date(string="Date d'attribution")
    peripheral_characteristics = fields.Text(string="Caractéristiques")

    components = fields.Boolean(string="Composant")
    components_grant_date = fields.Date(string="Date d'attribution")
    components_characteristics = fields.Text(string="Caractéristiques")

    cart_allowance = fields.Float(string="Prime de panier")
    transport_allowance = fields.Float(string="Indemnité de transport")
