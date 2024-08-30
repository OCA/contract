# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Contract Variable Quantity",
    "summary": """
        Product contract with variable quantity""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "depends": ["sale_management", "contract_variable_quantity", "product_contract"],
    "data": ["views/product_template.xml", "views/sale_order.xml"],
}
