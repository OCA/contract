# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract Sale Delivery Zone",
    "summary": """
        This module allows to ensure the delivery zone comes from the contract.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/contract",
    "maintainers": ["rousseldenis"],
    "depends": [
        "contract_delivery_zone",
        "contract_sale_generation",
        "partner_delivery_zone",
    ],
}
