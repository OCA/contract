# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Product Contract Line Defer",
    "summary": """Bridge between product_contract and contract_line_defer""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": [
        "product_contract",
        "contract_line_defer",
    ],
    "data": [
        "views/contract_line.xml",
        "views/product_template.xml",
        "views/sale_order.xml",
        "wizards/product_contract_configurator.xml",
    ],
    "assets": {"web.assets_backend": ["product_contract_line_defer/static/src/js/*"]},
    "auto_install": True,
}
