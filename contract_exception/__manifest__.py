# Copyright 2024 Foodles (http://www.foodles.co/)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Contract Exception",
    "version": "17.0.1.0.0",
    "category": "Contract Management",
    "author": "Odoo Community Association (OCA), Foodles",
    "website": "https://github.com/OCA/contract",
    "depends": [
        "base_exception",
        "contract",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/contract_exception_data.xml",
        "views/contract_views.xml",
        "wizard/contract_exception_confirm_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
