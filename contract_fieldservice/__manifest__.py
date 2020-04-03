# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Contract Fieldservice',
    'version': '12.0.1.0.0',
    'category': 'Fieldservice',
    'summary': 'This module allows you to set a service '
    'location on each line of the contract.',
    'author': 'Open Source Integrators, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/contract',
    'depends': [
        'contract_sale_invoicing',
        'fieldservice_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/contract_line.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': True,
}
