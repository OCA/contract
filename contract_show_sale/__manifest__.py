# -*- coding: utf-8 -*-
# Copyright (C) 2015 Angel Moya <angel.moya@domatix.com>
# Copyright (C) 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright (C) 2019 Sergio Corato (https://efatto.it)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Contract Show Sale',
    'summary': 'Button in contracts to show their sales',
    'version': '10.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'Sergio Corato,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/contract',
    'depends': ['analytic', 'sale'],
    'category': 'Sales Management',
    'data': [
        'views/contract_view.xml',
    ],
    'installable': True,
}
