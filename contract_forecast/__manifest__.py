# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract Forecast",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["contract_line_successor", "queue_job"],
    "data": [
        "data/queue_job_channel.xml",
        "data/queue_job_functions.xml",
        "security/contract_line_forecast_period.xml",
        "views/res_config_settings.xml",
        "views/contract_line_forecast_period.xml",
        "views/contract.xml",
    ],
    "maintainers": ["sbejaoui"],
    "post_init_hook": "post_init_hook",
}
