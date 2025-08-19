# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Partner Contract Anniversary",
    "summary": """
        This addon add a field for first contract line start date and compute
        contract anniversary date""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "category": "marketing",
    "website": "https://github.com/OCA/contract",
    "depends": [
        # OCA
        "contract",
    ],
    "external_dependencies": {
        "python": ["psycopg2"],
    },
    "data": [
        "views/res_partner.xml",
        "data/cron.xml",
    ],
    "maintainers": ["sbejaoui"],
    "installable": True,
}
