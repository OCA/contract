# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Sale Invoice Merge",
    "summary": """Adds a cron that creates merged invoices according to grouping
               fields.""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": [
        "product_contract",
        "queue_job_cron",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/contract_sale_invoice_merge_cron.xml",
        "data/queue_job_channel.xml",
        "data/queue_job_function.xml",
        "views/contract_contract.xml",
        "views/res_config_settings.xml",
    ],
}
