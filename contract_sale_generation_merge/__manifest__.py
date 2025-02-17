# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contracts Management - Recurring Sales Merge",
    "version": "15.0.1.0.0",
    "summary": "Merges contract lines into existing sale orders "
    "with the same commitment (delivery) date.",
    "category": "Contract Management",
    "website": "https://github.com/OCA/contract",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["ppyczko"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["contract_sale_generation"],
    "data": [
        "views/contract.xml",
    ],
}
