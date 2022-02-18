# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Sale Picking Tag",
    "summary": """
        Allows to use contract tags that were put to sales on stock pickings""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/contract",
    "depends": [
        "contract_sale_tag",
        "sale_stock",
    ],
    "data": [
        "views/stock_picking.xml",
    ],
}
