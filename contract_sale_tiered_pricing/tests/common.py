# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.sale_tiered_pricing.tests.common import TestTieredPricing


class TestContractTieredPricing(TestTieredPricing):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vals_cntrct_tmpl = {"name": "Test Contract Template"}
        cls.contract_template = cls.env["contract.template"].create(vals_cntrct_tmpl)

        cls.order.company_id.create_contract_at_sale_order_confirmation = True

        vals_product_contract = {
            "type": "service",
            "is_contract": True,
            "property_contract_template_id": cls.contract_template.id,
        }
        cls.product.write(vals_product_contract)

        vals_item_formula_with_discount = {
            "min_quantity": 0,
            "compute_price": "formula",
            "base": "pricelist",
            "base_pricelist_id": cls.pricelist.id,
            "price_discount": 50,
            "applied_on": "3_global",
        }
        cls.pricelist_formula_tier_based_discount = cls.env["product.pricelist"].create(
            {
                "name": "Discount based on a Tiered pricing",
                "is_tiered_pricing": False,
                "item_ids": [(0, 0, vals_item_formula_with_discount)],
                "discount_policy": "with_discount",
            }
        )
