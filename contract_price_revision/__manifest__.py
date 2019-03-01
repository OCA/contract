# Copyright 2019 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Contract Price Revision',
    'summary': 'Easy revision of contract prices',
    'version': '11.0.1.0.0',
    'category': 'Contract',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/contract',
    'depends': [
        'contract',
    ],
    'data': [
        'wizards/create_revision_line_views.xml',
        'views/account_analytic_account_views.xml',
    ],
    'installable': True,
}
