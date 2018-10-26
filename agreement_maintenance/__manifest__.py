# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Maintenance Agreements',
    'summary': 'Manage maintenance agreements and contracts',
    'author': 'Pavlov Media, '
              'Open Source Integrators, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/contract',
    'category': 'Partner',
    'license': 'AGPL-3',
    'version': '11.0.0.0.1',
    'depends': [
        'agreement',
        'maintenance',
        'fieldservice',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/agreement.xml',
        'views/agreement_serviceprofile.xml',
        'views/product.xml',
        'views/menu.xml',
    ],
    'application': False,
    'development_status': 'Beta',
    'maintainers': ['max3903'],
}
