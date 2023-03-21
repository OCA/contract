# Copyright 2023 Akretion - Florian Mounier
{
    "name": "Contract Price History",
    "summary": "This module historizes all contract line price changes.",
    "version": "14.0.1.0.0",
    "category": "Contract",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["contract"],
    "license": "AGPL-3",
    "post_init_hook": "_contract_line_price_history_post_init_hook",
    "data": [
        "security/ir.model.access.csv",
        "views/contract_line.xml",
    ],
    "installable": True,
}
