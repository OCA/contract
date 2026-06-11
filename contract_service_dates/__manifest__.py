# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Service Dates",
    "summary": """This module adds Service Dates fields to contract lines""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": [
        "contract",
    ],
    "data": [
        "views/contract_line.xml",
    ],
    "installable": True,
}
