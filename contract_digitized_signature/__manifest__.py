# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Contract Digitized Signature",
    "version": "11.0.1.0.0",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "category": "Contract Management",
    "license": "AGPL-3",
    "depends": [
        "contract",
        "sale",
        "web_widget_digitized_signature",
    ],
    "data": [
        "report/report_contract.xml",
        "views/contract_views.xml",
    ],
    "installable": True,
}
