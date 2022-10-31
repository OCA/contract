# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract Variable Qty Prorated",
    "summary": """
        This module adds a formula to compute prorated quantity to invoice as
        extension of the module contract_variable_quantity""",
    "version": "14.0.1.0.0",
    "development_status": "Beta",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["sbejaoui"],
    "website": "https://github.com/OCA/contract",
    "depends": ["contract_variable_quantity"],
    "data": [
        "data/contract_variable_qty_prorated.xml",
        "views/abstract_contract_view.xml",
    ],
    "demo": [],
}
