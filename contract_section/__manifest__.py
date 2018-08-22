# Copyright 2018 Road-Support - Roel Adriaans
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Contracts Management - Add section to invoice lines',
    'version': '11.0.1.0.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "Road-Support, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/oca/contract',
    'depends': [
        'contract',
        'sale'
    ],
    'data': [
        'views/account_analytic_account.xml',
        'views/account_analytic_contract.xml',
    ],
    'development_status': 'alpha',
    'installable': True,
}
