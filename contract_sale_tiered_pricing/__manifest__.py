# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale history",
    "summary": """
        Customer buying history used when computing the price.
        """,
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://acsone.eu",
    "depends": ["sale_tiered_pricing", "product_contract"],
    "data": [
        "data/sale_order_actions.xml",
        "views/sale_order.xml",
        "views/contract.xml",
    ],
}
