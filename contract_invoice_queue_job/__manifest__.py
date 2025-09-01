# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Invoice Queue Job",
    "summary": """Batch contract invoicing using queue job""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": [
        "contract",
        "queue_job",
    ],
    "data": [
        "data/ir_config_parameter_data.xml",
        "views/res_config_settings.xml",
        "wizards/contract_manually_create_invoice.xml",
    ],
}
