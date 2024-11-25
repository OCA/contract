# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract Last Date Update",
    "summary": """
        This module allows to update the last date invoiced if invoices are deleted.""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["contract"],
    "data": [
        "security/security.xml",
        "views/contract_views.xml",
        "views/contract_line.xml",
        "wizards/update_last_date_invoiced.xml",
    ],
    "maintainers": ["rafaelbn", "edlopen"],
}
