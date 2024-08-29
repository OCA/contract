# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Recurring - Product Contract",
    "version": "17.0.2.0.0",
    "category": "Contract Management",
    "license": "AGPL-3",
    "author": "LasLabs, " "ACSONE SA/NV, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["product", "contract", "sale"],
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
    "external_dependencies": {"python": ["dateutil"]},
    "maintainers": ["sbejaoui"],
    "assets": {"web.assets_backend": ["product_contract/static/src/js/*"]},
}
