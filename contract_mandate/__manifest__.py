# Copyright 2017 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract Mandate",
    "summary": "Mandate in contracts and their invoices",
    "version": "14.0.1.0.0",
    "author": "Odoo Community Association (OCA), " "Tecnativa",
    "website": "https://github.com/OCA/contract",
    "depends": ["contract_payment_mode", "account_banking_mandate"],
    "category": "Sales Management",
    "license": "AGPL-3",
    "data": ["views/contract_view.xml"],
    "installable": True,
    "auto_install": True,
}
