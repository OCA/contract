# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Agreements Legal Contract",
    "summary": "Create contract from agreement",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "category": "Agreement",
    "license": "AGPL-3",
    "version": "14.0.1.0.0",
    "depends": ["agreement_legal", "contract"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/create_contract_wizard.xml",
        "views/agreement_views.xml",
    ],
    "application": False,
    "development_status": "Beta",
    "maintainers": ["newtratip"],
}
