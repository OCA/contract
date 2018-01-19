# -*- coding: utf-8 -*-
# Copyright 2017-2018 Therp BV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Contract Line Extended',
    'version': '10.0.1.0.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "Therp BV, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/oca/contract',
    'depends': [
        'base_active_date',
        'contract',
    ],
    'data': [
        'views/account_analytic_account.xml',
    ],
    'installable': True,
}
