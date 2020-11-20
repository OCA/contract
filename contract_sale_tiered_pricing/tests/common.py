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
