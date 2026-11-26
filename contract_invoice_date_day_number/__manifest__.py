# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Invoice Date Day Number",
    "summary": """This module allows to define a defined date day number
    to use for the invoice date""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["base_partition", "contract"],
    "data": [
        "views/contract_contract.xml",
        "views/contract_template.xml",
    ],
}
