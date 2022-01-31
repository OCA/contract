# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract Sale Picking Note",
    "summary": """
        Allows to define picking notes on contract that will generate sale order""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": [
        "contract_sale_generation",
        "sale_stock_picking_note",
    ],
    "data": [
        "views/contract_contract.xml",
    ],
}
