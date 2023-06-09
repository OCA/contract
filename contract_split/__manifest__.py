# Copyright 2023 Damien Crier - Foodles
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Contract Split",
    "version": "14.0.1.0.0",
    "category": "Sales",
    "license": "AGPL-3",
    "summary": "Split contract",
    "depends": ["contract"],
    "author": "Foodles, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "data": [
        "security/ir.model.access.csv",
        "wizard/wizard_split_contract.xml",
        "views/contract.xml",
    ],
    "installable": True,
}
