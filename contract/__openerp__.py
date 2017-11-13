# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA (<http://openerp.com>)
# © 2016 Incaser Informatica S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Contracts Management recurring',
    'version': '9.0.1.0.0',
    'category': 'Other',
    'license': 'AGPL-3',
    'author': "OpenERP SA,"
              "Incaser Informatica S.L.,"
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
    'images': [],
}
