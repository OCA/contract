# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Product Contract Minimum Term",
    "summary": "Sell contract products with a minimum term instead of a fixed "
    "duration",
    "version": "18.0.1.0.0",
    "category": "Contract Management",
    "license": "AGPL-3",
    "author": "Callino,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "maintainers": ["wpichler"],
    "depends": ["product_contract", "contract_minimum_term"],
    "data": [
        "views/product_template.xml",
        "views/sale_order.xml",
        "wizards/product_contract_configurator_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "product_contract_minimum_term/static/src/js/*",
        ],
    },
    "auto_install": True,
}
