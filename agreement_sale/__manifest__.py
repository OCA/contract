# -*- coding: utf-8 -*-
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': u'Agreement (Sale)',
    'summary': "Link an agreement to a sale order and copy to invoice",
    'version': '10.0.1.0.1',
    'category': 'Contract',
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'depends': [
        'agreement_account',
        'sale_commercial_partner',
        ],
    'data': [
        'views/sale_order.xml',
        'views/agreement.xml',
        ],
    'installable': True,
    'auto_install': True,
}
