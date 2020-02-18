# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Agreement Legal Sale Fieldservice',
    'summary': 'Create an agreement when the sale order is confirmed',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Open Source Integrators, Odoo Community Association (OCA)',
    'category': 'Agreement',
    'website': 'https://github.com/OCA/contract',
    'depends': [
        'agreement_legal_sale',
        'fieldservice_agreement',
        'fieldservice_sale'
    ],
    'data': [
    ],
    'installable': True,
    'development_status': 'Beta',
    'maintainers': [
        'osi-scampbell',
        'max3903',
    ],
    'auto_install': True
}
