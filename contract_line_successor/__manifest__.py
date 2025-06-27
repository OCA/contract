# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Line Successor",
    "version": "18.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["contract"],
    "development_status": "Production/Stable",
    "maintainers": ["sbejaoui"],
    "data": [
        "data/contract_renew_cron.xml",
        "security/ir.model.access.csv",
        "views/contract_template.xml",
        "views/contract_contract.xml",
        "views/contract_template_line.xml",
        "views/contract_line.xml",
        "wizards/contract_line_wizard.xml",
        "views/res_config_settings.xml",
    ],
    "demo": [],
}
