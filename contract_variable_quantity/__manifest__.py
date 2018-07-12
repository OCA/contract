# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Variable quantity in contract recurrent invoicing',
    'version': '10.0.1.2.0',
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
