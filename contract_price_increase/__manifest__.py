# Copyright 2023 Akretion - Florian Mounier
{
    "name": "Contract Price Increase",
    "summary": "This module allows to increase all the prices of a contract.",
    "version": "14.0.1.0.0",
    "category": "Contract",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["contract"],
    "license": "AGPL-3",
    "data": [
        "data/contract_increase_cron.xml",
        "security/ir.model.access.csv",
        "views/contract.xml",
        "views/contract_increase.xml",
        "wizard/contract_increase_wizard_view.xml",
    ],
    "installable": True,
}
