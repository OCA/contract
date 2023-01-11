# Copyright 2023 elegosoft (https://www.elegosoft.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract Comments",
    "summary": "Comments texts templates on Contract documents",
    "version": "14.0.1.0.0",
    "category": "Contract Management",
    "author": "elego Software Solutions GmbH, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "contract",
        "account_comment_template",
    ],
    "data": [
        "views/contract_view.xml",
        "views/base_comment_template_view.xml",
        "views/report_contract.xml",
    ],
}
