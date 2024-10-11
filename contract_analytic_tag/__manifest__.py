# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Contract Analytic Tag",
    "version": "16.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/contract",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["contract", "account_analytic_tag"],
    "installable": True,
    "auto_install": True,
    "data": [
        "views/contract_views.xml",
        "views/contract_line_views.xml",
    ],
    "maintainers": ["victoralmau"],
}
