# -*- coding: utf-8 -*-
# Copyright 2014-2019 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Publication",
    "version": "10.0.1.0.0",
    "category": "Contract Management",
    "author": "Therp BV, " "Odoo Community Association (OCA)",
    "website": "https://github.com/oca/contract",
    "license": "AGPL-3",
    "summary": "Maintain electronic or print publications for your relations.",
    "depends": [
        "contract",
    ],
    "data": [
        "views/product_template.xml",
        "views/publication_distribution_list.xml",
        "views/res_partner.xml",
        "views/menu.xml",
        "security/ir.model.access.csv",
    ],
    "auto_install": False,
    "installable": True,
}
