# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Agreement',
    'summary': "Adds an agreement object",
    'version': '12.0.1.0.0',
    'category': 'Contract',
    'author': "Akretion,Odoo Community Association (OCA)",
    'contributors': 'Yves Goldberg (Ygol InternetWork)',
    'website': 'https://github.com/oca/contract',
    'license': 'AGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'security/agreement_security.xml',
        'views/agreement.xml',
        ],
    'demo': ['demo/demo.xml'],
    'installable': True,
}
