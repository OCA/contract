# -*- coding: utf-8 -*-
# © 2015 Angel Moya <angel.moya@domatix.com>
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Contract Show Invoice',
    'summary': 'Button in contracts to show their invoices',
    'version': '10.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'Domatix,'
              'Tecnativa,'
              'Odoo Community Association (OCA)',
    'website': 'http://www.domatix.com',
    'depends': ['account', 'analytic'],
    'category': 'Sales Management',
    'data': [
        'views/contract_view.xml',
    ],
    'installable': True,
}
