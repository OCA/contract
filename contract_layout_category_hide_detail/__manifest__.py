# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract Layout Category Hide Detail",
    "summary": """
        Allows to hide some section details that will be used also on invoices and sales.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": [
        "contract",
        "sale_layout_category_hide_detail",
    ],
    "data": ["views/contract.xml", "report/report_contract.xml"],
}
