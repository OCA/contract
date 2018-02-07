# coding: utf-8
# © 2018 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Agreement Sale Partner Invoice',
    'summary': "Define Invoiced Partner on Agreement object",
    'version': '10.0.1.0.0',
    'category': 'Contract',
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'depends': [
        'agreement_sale',
        ],
    'data': [
        'views/sale_order.xml',
        'views/agreement.xml',
        ],
    'demo': [
        'demo/demo.xml',
        ],
    'installable': True,
}
