# Copyright 2021 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Agreement Exception",
    "summary": "Custom exceptions on agreement",
    "version": "14.0.1.0.0",
    "category": "Contract",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["agreement_legal", "base_exception"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "data/agreement_exception_data.xml",
        "wizard/agreement_exception_confirm_view.xml",
        "views/agreement_view.xml",
    ],
    "installable": True,
}
