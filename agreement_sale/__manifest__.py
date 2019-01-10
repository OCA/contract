# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Agreement - Sale',
    'summary': 'Create an agreement when the sales order is confirmed',
    'version': '11.0.0.0.1',
    'license': 'AGPL-3',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'category': 'Agreement',
    'website': 'https://github.com/OCA/contract',
    'depends': [
        'agreement',
        'sale',
    ],
    'data': [
        'views/agreement.xml',
        'views/sale_order.xml'
    ],
    'installable': True,
    'development_status': 'Beta',
    'maintainers': [
        'osi-scampbell',
        'max3903',
    ],
}
