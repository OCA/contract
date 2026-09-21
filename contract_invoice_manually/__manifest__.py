# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Manually Invoice",
    "summary": """Option on contracts to invoice them manually""",
    "version": "18.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": [
        "contract",
    ],
    "data": [
        "views/contract_contract.xml",
        "views/res_config_settings.xml",
        "wizards/contract_manually_create_invoice.xml",
    ],
}
