# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Sale Tag",
    "summary": """
        Allows to transmit contract tags to sale order (through sale_generation)""",
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "maintainers": ["rousseldenis"],
    "depends": [
        "contract_sale_generation",
    ],
    "data": [
        "views/sale_order.xml",
    ],
}
