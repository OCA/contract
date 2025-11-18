# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Line Defer Successor",
    "summary": """Bridge Module contract_line_defer / contract_line_successor""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": [
        "contract_line_defer",
        "contract_line_successor",
    ],
    "data": [
        "views/contract_line.xml",
    ],
    "auto_install": True,
}
