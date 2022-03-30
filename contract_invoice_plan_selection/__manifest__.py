# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract Invoice Plan Selection",
    "version": "14.0.1.0.1",
    "category": "Contract Management",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/contract",
    "depends": ["contract_invoice_plan"],
    "data": [
        "security/ir.model.access.csv",
        "data/server_action.xml",
        "wizard/contract_make_planned_invoice_view.xml",
    ],
    "maintainers": ["kittiu"],
    "installable": True,
    "auto_install": True,
    "development_status": "Alpha",
}
