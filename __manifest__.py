# -*- coding: utf-8 -*-
{
    'name': "HR_REPORTS",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr','hr_gamification'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/payroll_report_wiz.xml',
        'data/hr_departements.xml',
        'data/hr_job.xml',
        #'data/salary_rules.xml',
        'views/attestation_de_travail_report.xml',
        'views/attestation_travail_template.xml',
        'views/certificat_de_travail_report.xml',
        'views/contrat_de_travail_report.xml',
        'views/views_inherit.xml',
        'views/attestation_de_stage.xml',
        'views/payroll_inherited_view.xml',
        'views/ats.xml',
        'views/fiche_de_poste.xml',
        'views/employee_inherited_view.xml',
        'views/declaration_de_reprise_du_travail.XML',
        'reports/hr_payroll_report.xml',
        'reports/payslip_report.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'application': False,
}
