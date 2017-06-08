# -*- coding: utf-8 -*-
# Copyright 2015 Domatix
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Contract Invoice Journal',
    'summary': 'Invoice Journal in contracts and their invoices',
    'version': '9.0.1.0.0',
    'author': 'Domatix, '
              'LasLabs, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.domatix.com',
    'depends': ['contract'],
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'data': [
        'views/contract.xml',
    ],
    'installable': True,
}
