# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Contract Termination",
    "summary": """contract_termination""",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["contract_line_successor"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/contract_terminate_reason.xml",
        "views/contract_contract.xml",
        "views/contract_terminate_reason.xml",
        "wizards/contract_contract_terminate.xml",
    ],
    "demo": [],
}
