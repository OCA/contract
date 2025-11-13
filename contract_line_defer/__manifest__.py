# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Line Defer",
    "summary": """Defer Contract Lines to avoid invoicing while start date unknown""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": [
        "contract",
    ],
    "data": [
        "security/contract_line_defer_disable.xml",
        "wizards/contract_line_defer_disable.xml",
        "views/contract.xml",
        "views/contract_line.xml",
        "views/res_config_settings.xml",
    ],
}
