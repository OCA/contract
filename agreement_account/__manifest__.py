# Copyright 2017-2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Agreement Account',
    'summary': "Agreement on invoices",
    'version': '12.0.1.0.0',
    'category': 'Contract',
    'author': 'Akretion, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/contract',
    'license': 'AGPL-3',
    'depends': [
        'agreement',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/agreement.xml',
        'views/account_invoice.xml',
        ],
    'development_status': 'Beta',
    'maintainers': [
        'alexis-via',
        'bealdav',
    ],
    'installable': True,
}
