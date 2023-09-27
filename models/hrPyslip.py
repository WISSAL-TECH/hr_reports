from odoo import models, fields, api
import random, string
from datetime import date, datetime, time
from odoo.exceptions import ValidationError
from odoo import http
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class WsPayslip(models.Model):
    _inherit = 'hr.payslip'



    nbr_hors_contract = fields.Integer(string="Jours hors contrat")
    out_contract = fields.Integer("Calcule salaire de jours hors contrat")
    checkInputs = fields.Boolean(default=True)
    salairePoste = fields.Float(string="salaire de poste")
    salaireImposable = fields.Float(string="salaire Imposable")
    totalGain = fields.Float(string="Total Gain")
    totalRetenu = fields.Float(string="TOTAL RETENUES")
    ruleOtherIds = fields.One2many('hr.salary.rule', 'payslipId')
    ruleIds = fields.One2many('hr.salary.rule', 'payslipId')
    ruleIds2 = fields.One2many('hr.salary.rule', 'payslipId')
    mode_pyment = fields.Selection([('ESPECE', 'ESPECE'),
                                    ('VERSEMENT', 'VERSEMENT')
                                    ], 'Mode de pyment', default='ESPECE')
    month = fields.Char(string='month', compute='_compute_current_month')

    def _compute_current_month(self):
        for record in self:
            month_name = record.date_to.strftime('%B')
            record.month = month_name


    # code structure paie
    codeJourTrav = '100'
    codeHorsup = 'WORK300'
    codeAbsence = 'LEAVE90'
    salaireBase = '100'
    iep = '103'
    primPanier = '207'
    primTrans = '210'
    fraisMission = '315'
    retenuSS = '201'
    irg = '301'
    listCodeOther = [fraisMission]
    listCodeJourTravailer = [codeJourTrav, codeHorsup, codeAbsence]
    listCodeGain = [salaireBase, iep, primPanier, primTrans, fraisMission]
    listCodeRetenues = [retenuSS, irg]



    @api.onchange('contract_id', 'struct_id')
    def Hrline(self):
        for rec in self:
            if rec.contract_id:
                rec.worked_days_line_ids = [(5, 0, 0)]





    @api.onchange('struct_id')
    def getListIdsRule(self):
        """
        function qui met a jour le filter des rule de paiment (structure de paie)
        """
        if self.employee_id.name:
            rules = self.struct_id.rule_ids
            idsRule = []
            idsRule2 = []
            test = False
            test2 = False
            if rules:
                for rule in rules:
                    if rule.code in self.salaireBase:
                        idsRule.append(rule.id)
                        test = True
                    if rule.code in self.listCodeOther:
                        idsRule2.append(rule.id)
                        test2 = True
                    if test:
                        for rec in self:
                            rec.ruleIds = idsRule
                    else:
                        for rec in self:
                            rec.ruleIds = None

                    if test2:
                        for rec in self:
                            rec.ruleIds2 = idsRule2
                    else:
                        for rec in self:
                            rec.ruleIds2 = None

    def calTotalGainWcm(self):
        """
        function qui calcul le salaire total gagnée
        """
        self.totalGain = 0
        if self.checkEntryWCM():
            for rec in self.line_ids:
                if rec.code in self.listCodeGain:
                    self.totalGain += rec.total
        return self.totalGain

    def calTotalRetenuesWcm(self):
        """
        function qui calcul le salaire total retenus
        """
        self.totalRetenu = 0
        if self.checkEntryWCM():
            for rec in self.line_ids:
                if rec.code in self.listCodeRetenues:
                    self.totalRetenu += rec.total
        return self.totalRetenu
    def calSalairePoste(self):
        """
            function qui calcule le le salire de poste
        """
        salairePoste = 0
        for line in self.line_ids:
            if line.code in [self.salaireBase, self.iep]:
                salairePoste+=line.total

        self.salairePoste = salairePoste
        return salairePoste

    @api.onchange("worked_days_line_ids")
    def checkWorkLine(self):
        if self.employee_id.name:
            if len(self.worked_days_line_ids.ids) <= 0:
                self.checkInputs = True

    @api.constrains("worked_days_line_ids")
    def checkButtonTimeSheet(self):
        if self.employee_id.name:
            for rec in self:
                if rec.worked_days_line_ids:
                    rec.checkInputs = False
                else:
                    rec.checkInputs = True

    def getContratOpen(self):
        today = datetime.today()
        contrat_employee = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id),
             ('date_start', '<=', today.date()), ('state', '=', 'open')], limit=1)
        contrat_id = None
        if contrat_employee:
            for rec in contrat_employee:
                contrat_id = rec
                break
        return contrat_id

    def getNumberDaysWork(self):
        today = datetime.today()
        """
        function qui recupere le nombre de jour travailler d'une employee
        number de jour present
        """
        list_prestation = self.env['hr.work.entry'].search([
            ('date_start', '>=', datetime(self.date_from.year, self.date_from.month, self.date_from.day)),
            ('date_stop', '<=', datetime(self.date_to.year, self.date_to.month, self.date_to.day)),
            ('employee_id', '=', self.employee_id.id),
            ('work_entry_type_id.code', '=', self.codeJourTrav)
        ])
        nbr_jour = 0
        nbr_heure = 0
        if list_prestation:
            new_list_timesheet = []
            for i in list_prestation:
                nbr_heure += i.duration
                nbr_jour = round(nbr_heure / 8, 2)

        else:
            error = ValidationError(f'La feuille de temps de {self.employee_id.name}'
                                    f' du {self.date_from} au {self.date_to}, ne comporte aucune journée de travail.')
            # afficher un message que la prestation est vide
            raise error
        return nbr_jour



    def ImportPrestation(self):
        today = datetime.today()
        jourTravail = self.getNumberDaysWork()
        if self.contract_id:
            contrat_res = self.contract_id
        contrat_id = contrat_res.id
        date = self.date_from
        list_payslip = self.env['hr.payslip'].search([])
        if list_payslip:
            for i in list_payslip:
                id_payslip = i.id
                break
        else:
            id_payslip = 0
        dayabsence = self.getdayabsenceEMP()
        print(dayabsence)
        if dayabsence != 0:
            id_dayBS = self.env['hr.work.entry'].search([
                ('date_start', '>=', datetime.combine(self.date_from, time.min)),
                ('date_stop', '<=', datetime.combine(self.date_to, time.min)),
                ('employee_id', '=', self.employee_id.id),
                ('work_entry_type_id.code', '=', self.codeAbsence)
            ], limit=1)
            print("je suis la")
            ABSDAY = {
                    'payslip_id': id_payslip,
                    'work_entry_type': id_dayBS.work_entry_type_id.id,
                    'code':self.codeAbsence,
                    'number_of_hours': dayabsence,
                    'number_of_days': round(dayabsence / 8, 2),
                    'contract_id': contrat_id,
            }
        if jourTravail != 0:
            id_jrT = self.env['hr.work.entry'].search([
                ('date_start', '>=', datetime.combine(self.date_from, time.min)),
                ('date_stop', '<=', datetime.combine(self.date_to, time.min)),
                ('employee_id', '=', self.employee_id.id),
                ('work_entry_type_id.code', '=', self.codeJourTrav)
            ], limit=1)
            jrTravail = {
                    'payslip_id': id_payslip,
                'code': self.codeJourTrav,
                'work_entry_type': id_jrT.work_entry_type_id.id,
                    'number_of_hours': round(jourTravail * 8, 2),
                    'number_of_days': jourTravail,
                    'contract_id': contrat_id,
            }
        else:
            jrTravail = None
        vals = [
            jrTravail,
        ]
        for val in vals:
            env = self.env['hr.payslip.worked_days'].create(val)
            self.worked_days_line_ids += env


    def getSalareParDays(self):
        """
            functoin qui calcule le salaire par jour elle prend le id de la employee comme
            param elle retourne une valure(salaire de base / 22).
        """
        today = date.today()
        contrats = self.env['hr.contract'].search(['|', ('date_end', '>', today),
                                                   ('date_end', '=', False),
                                                   ('state', '=', 'open'),
                                                   ('employee_id', '=', self.employee_id.id)])
        contrat = False
        if contrats:
            for rec in contrats:
                contrat = rec
                break

        if contrat:
            return contrat.wage
        else:
            return False

    def getdayabsenceEMP(self):

        today = datetime.today()
        prestation = self.env['hr.work.entry'].search([
            ('date_start', '>=', datetime(self.date_from.year, self.date_from.month, self.date_from.day)),
            ('date_stop', '<=', datetime(self.date_to.year, self.date_to.month, self.date_to.day)),
            ('employee_id', '=', self.employee_id.id),
            ('work_entry_type_id.code', '=', self.codeAbsence)])
        amount = 0
        print("Hello nadjet")
        print(prestation)
        if prestation:
            for rec in prestation:
                amount+= round(rec.duration , 4)

        return amount

    def getHoursup(self):
        """
        function qui retourne les jour suplimentaire X2 d'une employee
        elle prend trois param date debut, fin et employee_id
        """
        timesheet = self.env['hr.work.entry'].search([('date_start', '>=', datetime.combine(self.date_from, time.min)),
                                                      ('date_stop', '<=', datetime.combine(self.date_to, time.min)),
                                                      ('employee_id', '=', self.employee_id.id),
                                                      ('work_entry_type_id.code', '=', self.codeHorsup)])
        amount = 0
        if timesheet:
            for rec in timesheet:
                amount+= rec.duration
        return amount

    def getPaieAbsence(self, date_debut, date_fin, res):
        """
            function qui calcule le salaire d'absence d'une employee elle prend 3 params
            date de debut et fin (la peroid que on veux calculer) e le id de la employee elle
            retourne le montant de salaire d'absence.
        """
        # import timesheet
        pristation_count = self.env['hr.work.entry'].search_count([('date_start', '>=', date_debut),
                                                                          ('date_stop', '<=', date_fin),
                                                                          ('employee_id', '=', res),
                                                                          ('work_entry_type_id.code', '=', 'LEAVE90')])
        wage = self.getSalareParDays(res)
        if wage:
            wageDays = wage / 22
            wageDays = round((wageDays), 4)
            return wageDays
        else:
            return 0

    def get_paie_out_contract(self, date_debut, date_fin, res):
        """
            function qui calcule le salaire des jours hors contrat
        """

        wage = self.getSalareParDays(res)
        if wage:
            wageDays = wage / 22
            salary_out_contract = round((self.nbr_hors_contract * wageDays), 4)
            return salary_out_contract
        else:
            return 0

    def action_payslip_done(self):
        """
            modification sur la function de base de confirmer le calcul la feuille de paie
        """
        res = super().action_payslip_done()
        return res


    def checkEntryWCM(self):
        """Function qui verfier les entrée du jour de travail
        elle retourne False(il y a un manque) ou True(si tu vas bien)"""
        test = False
        print("Hello world")
        print(self.worked_days_line_ids)
        if self.worked_days_line_ids:
            for rec in self.worked_days_line_ids:
                if rec.code == self.codeJourTrav:
                    test = True
                    break
        return test

    def getYearExpEMP(self):
        """Function qui return le nombre d'année d'experience de l'employe """

        today = date.today().year
        cr = self._cr
        res_id = self.employee_id.id
        sql = f"SELECT MIN(date_start) FROM hr_contract WHERE  employee_id = {res_id}"
        cr.execute(sql)
        result = self.env.cr.fetchall()
        if result[0][0]:
            date_start = result[0][0]
            year = date_start.year
            print(date_start.year, "contra exp")
            print(today - year, "year exp")
            return today - year
        else:
            return 0

    def calSalaireBaseWcm(self):
        """
            function qui calcule le salaire de base d'un employée(employee)
        """
        salaireBase = 0
        for rec in self.worked_days_line_ids:
            # cas de salaire de base
            if rec.code == self.codeJourTrav:
                for line in self.line_ids:
                    if line.code == self.codeJourTrav:
                        line.quantity = rec.number_of_days
                        line.rate = round(1, 2)
                        amount = round(self.contract_id.wage / 22, 2)
                        line.amount = amount
                        line.total = amount * line.quantity
                        salaireBase = line.total
                        break
        return salaireBase

    def calSalaireImposable(self):
        """
            function qui return le salaire Imposable d'une employee
        """
        salaireImposable = 0
        salairePoste = self.calSalairePoste()
        rss = 0
        for line in self.line_ids:
            if line.code == self.retenuSS:
                rss = line.total
                break
        alocation = 0
        for line in self.line_ids:
            if line.code in [self.primTrans, self.primPanier]:
                alocation += line.total
        salaireImposable = salairePoste - rss + alocation
        self.salaireImposable = salaireImposable
        return salaireImposable




    def calHoursSup(self):
        """
            function qui calculer les heure suplimentaire d'une employee
            """
        for rec in self.worked_days_line_ids:

            if rec.code == self.codeHorsup:
                for line in self.line_ids:
                    if line.code == "WORK300":
                        line.quantity = rec.number_of_hours
                        line.rate = round(1, 2)
                        line.amount = round((self.contract_id.cout_hours * 1.5), 4)
                        line.total = round(line.amount * line.quantity, 4)
                        break





    def calFraiMission(self):
        """
        function qui calculer le total des frais de mission
        """
        test = False
        for line in self.line_ids:
            if line.code == self.salaireBase:
                test = True
                break
        if test:
            if self.input_line_ids:
                for rec in self.input_line_ids:
                    if rec.code == self.fraisMission:
                        for line in self.line_ids:
                            if line.code == self.fraisMission:
                                line.quantity = 1
                                line.rate = round(1, 2)
                                line.amount = rec.amount
                                line.total = rec.amount
                                break
    @api.onchange('struct_id')
    def changeStruct(self):
        if self.line_ids:
            raise ValidationError("Erreur : Impossible de modifier la structure d'une feuille de paie déjà calculée.")


    def getYearExperEMP(self):
        """Function qui return le nombre d'année d'experience de l'employe """

        today = date.today().year
        cr = self._cr
        res_id = self.employee_id.id
        sql = "select min(date_start) from hr_contract where employee_id = "+str(res_id)
        cr.execute(sql)
        result = self.env.cr.fetchall()
        if result[0][0]:
            date_start = result[0][0]
            year = date_start.year
            return today - year
        else:
            return 0

    def calSalaireIEPWcm(self):
        """
            function qui calcule le salaire IEP
        """
        salaireBase = self.calSalaireBaseWcm()
        for line in self.line_ids:
            if line.code == self.iep:
                line.quantity = self.getYearExperEMP()
                yearExp = line.quantity
                line.amount = salaireBase
                line.rate = round(1, 2)
                line.total = round(salaireBase * yearExp / 100, 2)
                break
    def calSalaireRSS(self):
        """
        function qui calcule le salaire retenu sociale
        """
        iep = 0
        for line in self.line_ids:
            if line.code == self.iep:
                iep = line.total
                break
        salaireBase = 0
        for line in self.line_ids:
            if line.code == self.salaireBase:
                salaireBase += line.total
        for line in self.line_ids:
            if line.code == self.retenuSS:
                line.amount = salaireBase + iep
                self.salairePoste = line.amount
                line.rate = round(9, 2)
                line.quantity = None
                line.total = round((line.amount * 9) / 100, 4)
                break
    def calAlocation(self):
        """
        function qui calcule le salaire allocation(prime...)
        """
        for line in self.line_ids:
            qte = 0
            if line.code == self.salaireBase:
                qte = line.quantity
                break
        for line in self.line_ids:
            if line.code == self.primTrans:
                line.quantity = qte
                line.rate = round(1, 2)
                line.amount = round(self.contract_id.travel_allowance, 4)
                line.total = round(line.amount * line.quantity, 4)
            if line.code == self.primPanier:
                line.quantity = qte
                line.rate = round(1, 2)
                line.amount = round(self.contract_id.meal_allowance, 4)
                line.total = round(line.amount * line.quantity, 4)
    def calIRG(self):
        """
        function qui calcule le salaire IRG
        """
        salaire = int(self.calSalaireImposable())
        salaire = str(salaire)
        updateSalaire = list(salaire)
        updateSalaire[-1] = '0'
        newSalaire = ''.join(updateSalaire)
        newSalaire = int(newSalaire)
        irg = self.env['bareme.irg'].search([('irg_salaire_imposable','>=', newSalaire),('irg_salaire_imposable','<=', newSalaire)])
        if irg:
            salaireImposable = 0
            salaireRSS = 0
            for line in self.line_ids:
                if line.code == self.retenuSS:
                    salaireImposable = line.amount - line.total
                    break
            for line in self.line_ids:
                if line.code == self.primPanier or line.code == self.primTrans:
                    salaireImposable += line.total
                    self.salaireImposable = salaireImposable
            for line in self.line_ids:
                if line.code == self.irg:
                    line.amount = salaireImposable
                    line.quantity = 1
                    line.rate = round(1, 2)
                    line.total = irg.irg_regime_general



    def calculPaie(self):
        """
            function qui calcule la paie d'un employer de wcm
        """
        # calculer le salaire de base:
        self.calSalaireBaseWcm()
        # caculer les heure sup:
        self.calHoursSup()
        # calculer les autre entrée(frais de mission)
        self.calFraiMission()
        #calculer le salaire IEP code '103':
        self.calSalaireIEPWcm()
        #calculer le salaire retrnu SS code '201':
        self.calSalaireRSS()
        #calculer la prime de transport et la prime de panier
        self.calAlocation()
        #calculer le salaire irg
        self.calIRG()
        #calculer le total gain et total retenu et:
        self.calTotalGainWcm()
        self.calTotalRetenuesWcm()




    def deleteNullEntry(self):
        """
        function qui elimine les entrée null
        """
        for rec in self.line_ids:
            if rec.total == 0:
                rec.unlink()
        return True


    @api.onchange('line_ids')
    def updateVals(self):
        if self.employee_id.name:
            if self.ids:
                id = self.ids[0]
                objet = self.env['hr.payslip'].browse(id)
                if not self.line_ids:
                    objet.write({'totalGain': 0, 'totalRetenu': 0, 'salairePoste': 0,'salaireImposable': 0})
                else:
                    totalGain = self.calTotalGainWcm()
                    totalReatenu =self.calTotalRetenuesWcm()
                    salairePoste = self.calSalairePoste()
                    salaireImposable = self.calSalaireImposable()
                    objet.write({'totalGain': totalGain, 'totalRetenu': totalReatenu, 'salairePoste': salairePoste,
                                 'salaireImposable': salaireImposable})

    def compute_sheet(self):
        """
                    modification sur la function de base de calculer la feuille de paie
                """
        if self.employee_id.name:
            res = False
            if self.checkEntryWCM():
                res = super().compute_sheet()
                self.calculPaie()
                self.deleteNullEntry()
            else:
                self.totalRetenu = 0
                self.totalGain = 0
                self.salairePoste = 0
                self.salaireImposable = 0
        else:
            return super().compute_sheet()


class WsPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'


    rate = fields.Float(string='Rate (%)', digits=(16, 2), default=1.0)



class PayslipWorked_days(models.Model):
    _inherit = 'hr.payslip.worked_days'

    work_entry_type  = fields.Many2one('hr.work.entry.type', 'Type de jour')
    name = fields.Char(string='Description', required=False, related= 'work_entry_type.name')
    contract_id = fields.Many2one('hr.contract', required=False, string='Contract')
    code = fields.Char(required=False, related='work_entry_type.code')
    @api.onchange('number_of_days')
    def updateHours(self):
        for rec in self:
            rec.number_of_hours = round(rec.number_of_days * 8, 4)

    @api.onchange('number_of_hours')
    def updateDays(self):
        for rec in self:
            rec.number_of_days = round(rec.number_of_hours / 8, 4)

class InputeLineIDS(models.Model):
    _inherit = 'hr.payslip.input'

    name = fields.Many2one('hr.salary.rule', string='Description', required=False)
    salaryRule = fields.Many2one('hr.salary.rule', string='Description')
    contract_id = fields.Many2one('hr.contract', related='payslip_id.contract_id')
    code = fields.Char(required=False, related='salaryRule.code')

class RuleLine(models.Model):
    _inherit = 'hr.salary.rule'

    payslipId = fields.Many2one('hr.payslip')