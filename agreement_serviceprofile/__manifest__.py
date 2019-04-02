# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Agreement Service Profile',
    'summary': "Adds an Agreement Service Profile object",
    'version': '12.0.1.0.0',
    'category': 'Contract',
    'author': 'Pavlov Media, '
              'Open Source Integrators, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/oca/contract',
    'license': 'AGPL-3',
    'depends': ['agreement_legal'],
    'data': [
        'security/ir.model.access.csv',
        'views/agreement_serviceprofile.xml',
    ],
    'development_status': 'Beta',
    'maintainers': [
        'max3903',
    ],
    'installable': True,
}
