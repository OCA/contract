# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract Product Set Layout",
    "summary": """
        Allows to manage correctly product set layout lines with
        contract_product_set module.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/contract",
    "depends": [
        "sale_product_set_layout",
        "contract_product_set",
    ],
    "data": [
        "wizards/product_set_add_contract.xml",
    ],
    "auto_install": True,
}
