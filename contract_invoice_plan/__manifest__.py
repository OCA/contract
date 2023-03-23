# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Contract Invoice Plan",
    "summary": "Add to contract, ability to manage future invoice plan",
    "version": "15.0.1.0.0",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/contract",
    "category": "Contract Management",
    "depends": ["contract"],
    "data": [
        "security/ir.model.access.csv",
        "data/contract_data.xml",
        "wizard/contract_create_invoice_plan_view.xml",
        "wizard/contract_make_planned_invoice_view.xml",
        "views/contract_view.xml",
    ],
    "installable": True,
    "maintainers": ["kittiu"],
    "development_status": "Alpha",
}
