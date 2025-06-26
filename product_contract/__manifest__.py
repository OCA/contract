# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Recurring - Product Contract",
    "version": "18.0.1.0.0",
    "category": "Contract Management",
    "license": "LGPL-3",
    "author": "LasLabs, " "ACSONE SA/NV, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["product", "contract_termination", "sale"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/res_config_settings.xml",
        "views/contract.xml",
        "views/product_template.xml",
        "views/sale_order.xml",
        "wizards/product_contract_configurator_views.xml",
    ],
    "installable": True,
    "application": False,
    "external_dependencies": {"python": ["python-dateutil"]},
    "maintainers": ["sbejaoui"],
    "assets": {"web.assets_backend": ["product_contract/static/src/js/*"]},
}
