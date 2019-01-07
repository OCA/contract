# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Contract Sale Payment Mode',
    'summary': """
        This addon manages payment mode from sale order to contract.""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu/',
    'depends': [
        # OCA/bank-payment
        'account_payment_sale',
        # OCA/contract
        'product_contract',
    ],
    'data': [
    ],
    'demo': [
    ],
}
