# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Contract - Auto Payment",
    "summary": "Adds automatic payments to contracts.",
    "version": "12.0.1.0.0",
    "category": "Contract Management",
    "license": "AGPL-3",
    "author": "LasLabs, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": [
        "contract",
        "payment",
    ],
    "data": [
        "data/mail_template_data.xml",
        "data/ir_cron_data.xml",
        "views/contract_view.xml",
        "views/contract_template_view.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
    "application": False,
}
