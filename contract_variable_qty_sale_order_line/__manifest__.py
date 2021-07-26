# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Contract Variable Qty Sale Order Line',
    'summary': """
        This module adds a formula to compute sale order line quantity to
        invoice as extension of the module contract_variable_quantity""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Escodoo,Odoo Community Association (OCA)',
    'category': 'Contract Management',
    'maintainers': ['marcelsavegnago'],
    'images': ['static/description/banner.png'],
    'website': 'https://github.com/OCA/contract',
    'depends': [
        'product_contract_variable_quantity',
    ],
    'data': [
        'data/contract_variable_qty_sale_order_line.xml',
    ],
}
