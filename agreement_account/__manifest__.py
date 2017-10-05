# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': u'Agreement (Account)',
    'summary': "Adds an agreement object linked to an invoice",
    'version': '10.0.1.0.0',
    'category': 'Contract',
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'security/agreement_security.xml',
        'views/agreement.xml',
        'views/account_invoice.xml',
        ],
    'demo': ['demo/demo.xml'],
    'installable': True,
}
