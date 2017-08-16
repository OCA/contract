# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Contracts Management - Recurring',
    'version': '10.0.1.1.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "OpenERP SA, "
              "Tecnativa, "
              "LasLabs, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/oca/contract',
    'depends': ['base', 'account', 'analytic'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_contract.xml',
        'report/contract_views.xml',
        'data/contract_cron.xml',
        'data/mail_template.xml',
        'views/account_analytic_account_view.xml',
        'views/account_analytic_contract_view.xml',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
}
