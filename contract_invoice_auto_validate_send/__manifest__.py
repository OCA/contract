# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Invoice Auto Validate Send",
    "summary": """
        Send the automatically validated contract invoice to the customer""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": [
        "contract_invoice_auto_validate",
    ],
    "data": [
        "views/res_config_settings.xml",
    ],
}
