# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract Forecast",
    "summary": """
    Contract forecast""",
    "version": "12.0.1.0.3",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["base", "contract", "queue_job"],
    "data": [
        "security/contract_line_forecast_period.xml",
        "views/contract_line_forecast_period.xml",
        "views/contract.xml",
    ],
    "external_dependencies": {"python": ["dateutil"]},
    "post_init_hook": "post_init_hook",
}
