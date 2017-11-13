# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Contracts Management recurring',
    'version': '9.0.1.0.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "OpenERP SA,"
              "Tecnativa,"
              "Odoo Community Association (OCA)",
    'website': 'http://openerp.com',
    'depends': ['base', 'account', 'analytic'],
    'data': [
        'security/ir.model.access.csv',
        'data/contract_cron.xml',
        'views/contract.xml',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
}
