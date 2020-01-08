# Copyright 2016-2019 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Variable quantity in contract recurrent invoicing',
    'version': '12.0.2.1.2',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "Tecnativa,"
              "Odoo Community Association (OCA)",
    'website': 'https://www.tecnativa.com',
    'depends': ['contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/abstract_contract_line.xml',
        'views/contract_line_formula.xml',
        'views/contract_line_views.xml',
        'views/contract_template.xml',
        'views/contract.xml',
    ],
    'installable': True,
}
