# -*- coding: utf-8 -*-
# Copyright 2016 Binovo IT Human Project SL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Contract Account Banking Mandate",
    "version": "8.0.1.0.0",
    "depends": [
        "account_analytic_analysis", "account_banking_mandate"
    ],
    "author": "Binovo IT Human Project SL, Odoo Community Association (OCA)",
    "category": 'Sales Management',
    "website": "http://www.binovo.es",
    "summary": "Add banking mandate field to contracts for their invoices",
    "data": [
        "views/contract_view.xml",
    ],
    "test": [
        "tests/contract_account_banking_mandate.yml"
    ],
    "installable": True,
    "auto_install": False,
}
