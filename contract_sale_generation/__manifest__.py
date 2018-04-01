# -*- coding: utf-8 -*-
# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)


{
    'name': 'Contracts Management - Recurring Sales',
    'version': '10.0.3.0.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "PESOL, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/oca/contract',
    'depends': ['contract', 'sale'],
    'data': [
        'views/account_analytic_account_view.xml',
        'views/account_analytic_contract_view.xml',
        'views/sale_view.xml',
        'data/contract_cron.xml',
    ],
    'installable': True,
}
