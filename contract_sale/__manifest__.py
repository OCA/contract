# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Contract from Sale',
    'version': '10.0.1.0.0',
    'category': 'Sales',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/contract',
    'depends': [
        'sales_team',
        'contract',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/account_analytic_account_security.xml',
        'views/account_analytic_account_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': True,
}
