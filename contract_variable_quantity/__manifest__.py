# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Variable quantity in contract recurrent invoicing',
    'version': '11.0.1.3.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "Tecnativa,"
              "Odoo Community Association (OCA)",
    'website': 'https://www.tecnativa.com',
    'depends': [
        'contract',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/contract_view.xml',
    ],
    'installable': True,
}
