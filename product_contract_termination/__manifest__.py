{
    "name": "Termination - Product Contract",
    "version": "18.0.1.0.0",
    "category": "Contract Management",
    "license": "AGPL-3",
    "author": "LasLabs, " "ACSONE SA/NV, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["sale", "product", "product_contract", "contract_termination"],
    "data": [
        "views/product_template.xml",
        "views/sale_order.xml",
        "wizards/product_contract_configurator_views.xml",
    ],
    "installable": True,
    "application": False,
    "external_dependencies": {"python": ["python-dateutil"]},
    "maintainers": ["sbejaoui"],
    "assets": {
        "web.assets_backend": [
            "product_contract_termination/static/src/js/contract_configurator_controller.esm.js",
            "product_contract_termination/static/src/js/sale_product_field.esm.js",
        ],
    },
}
