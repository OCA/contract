# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Layout Category Hide Detail",
    "summary": "Hide details for sections in contracts and their reports, "
    "portal and generated invoices",
    "category": "Contract Management",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": [
        "sale_layout_category_hide_detail",
        "product_contract_section",
    ],
    "data": [
        "views/contract_template_line.xml",
        "views/contract.xml",
        "views/contract_portal_templates.xml",
        "report/report_contract.xml",
    ],
}
