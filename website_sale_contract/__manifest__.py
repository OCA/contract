# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Website Sale Contract",
    "summary": "Extends checkout sale process with signing contracts",
    "version": "10.0.1.0.0",
    "category": "Contract",
    "website": "https://laslabs.com",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale",
        "website_portal_contract",
        "product_contract",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/contract_checkout_templates.xml",
        "views/assets.xml",
    ],
    "demo": [
        "demo/product_product_demo.xml",
        "demo/sale_order_demo.xml",
        "demo/sale_order_line_demo.xml",
    ],
}
