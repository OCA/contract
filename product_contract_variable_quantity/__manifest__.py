# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Product Contract Variable Quantity",
    "summary": """
        Product contract with variable quantity""",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["contract_variable_quantity", "product_contract"],
    "data": [
        "views/product_template.xml",
        "views/sale_order.xml",
        "wizards/product_contract_configurator.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": ["product_contract_variable_quantity/static/src/js/*"]
    },
}
