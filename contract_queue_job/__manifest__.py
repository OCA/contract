# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract Queue Job",
    "summary": """
        This addon make contract invoicing cron plan each contract in a job
        instead of creating all invoices in one transaction""",
    "version": "15.0.1.1.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["contract", "queue_job"],
    "maintainers": ["sbejaoui"],
}
