# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Timesheet",
    "summary": """
        Link projects to sale contracts""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": [
        "contract",
        "sale_project",
        "sale_timesheet",
    ],
    "data": [
        "views/project_project.xml",
    ],
    "maintainer": ["sbidoul"],
}
