# Copyright 2024 Kmee
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract HR - Freelancer/Contractor Contracts",
    "version": "16.0.1.0.0",
    "category": "Contract Management",
    "license": "AGPL-3",
    "author": "KMEE, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["contract", "hr_contract"],
    "development_status": "Alpha",
    "data": [
        "views/contract_views.xml",
        "views/hr_employee_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
