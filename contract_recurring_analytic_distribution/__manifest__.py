# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Analytic plans on contracts recurring invoices',
    'version': '10.0.1.0.0',
    'category': 'Contract Management',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/contract/',
    'license': 'AGPL-3',
    'depends': [
        'account_analytic_distribution',
        'contract',
    ],
    'data': [
        'views/account_analytic_invoice_line_view.xml',
    ],
    'installable': True,
}
