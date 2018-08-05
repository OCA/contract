# -*- coding: utf-8 -*-
# Copyright 2018 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Contract Cancel",
    "summary": "Auto cancel contracts if past due invoices.",
    "version": "10.0.1.0.0",
    "category": "Contract Management",
    'website': 'https://github.com/oca/contract',
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "contract",
    ],
    "data": [
        "views/account_analytic_account_view.xml",
        "views/account_analytic_contract_view.xml",
    ],
}
