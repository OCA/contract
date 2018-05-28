# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Contract - Auto Payment",
    "summary": "Adds automatic payments to contracts.",
    "version": "10.0.1.0.1",
    "category": "Contract Management",
    "license": "AGPL-3",
    "author": "LasLabs, "
              "Odoo Community Association (OCA)",
    "website": "https://laslabs.com",
    "depends": [
        "contract",
        "payment",
    ],
    "data": [
        "data/mail_template_data.xml",
        "data/ir_cron_data.xml",
        "views/account_analytic_account_view.xml",
        "views/account_analytic_contract_view.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
    "application": False,
}
