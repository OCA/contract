# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Contract Invoicing of Pending Sales Orders",
    "summary": "Include sales to invoice in contract invoice creation",
    "version": "14.0.1.0.0",
    "category": "Contract Management",
    "website": "https://github.com/OCA/contract",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "contract",
        "sale_management",
    ],
    "data": [
        "views/contract_view.xml",
    ],
}
