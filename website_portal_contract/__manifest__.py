# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Website Portal Contract",
    "summary": "Extends website portal with contracts.",
    "version": "10.0.1.0.0",
    "category": "Contract Management",
    "website": "https://laslabs.com",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "contract",
        "contract_show_invoice",
        "website_quote",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/website_contract_template_data.xml",
        "views/account_analytic_account_view.xml",
        "views/account_analytic_contract_template_view.xml",
        "views/account_analytic_contract_view.xml",
        "views/website_portal_contract_templates.xml",
    ],
    "demo": [
        # Load order must be `contract => account => invoice line`
        "demo/account_analytic_contract_demo.xml",
        "demo/account_analytic_account_demo.xml",
        "demo/account_analytic_invoice_line_demo.xml",
        "demo/assets_demo.xml",
    ],
}
