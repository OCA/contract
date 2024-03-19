# Copyright 2023 Foodles (http://www.foodles.co/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractDiscounts(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.contract4 = cls.env["contract.contract"].create(
            {
                "name": "Test Contract4",
                "partner_id": cls.partner.id,
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "line_recurrence": True,
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_1.id,
                            "name": "Services from #START# to #END#",
                            "quantity": 1,
                            "uom_id": cls.product_1.uom_id.id,
                            "price_unit": 100,
                            "discount_fixed": 48,
                            "recurring_rule_type": "monthly",
                            "recurring_interval": 1,
                            "date_start": "2018-02-15",
                            "recurring_next_date": "2018-02-22",
                        },
                    )
                ],
            }
        )

    def test_onchange_discount(self):
        contract = Form(self.contract)
        line = contract.contract_line_ids.edit(0)
        line.discount_fixed = 42
        self.assertFalse(line.discount)

    def test_onchange_discount_fixed(self):
        contract = Form(self.contract)
        line = contract.contract_line_ids.edit(0)
        line.discount = 42
        self.assertFalse(line.discount_fixed)

    def test_constraint_discount_discount_fixed(self):
        with self.assertRaisesRegex(
            ValidationError, "You can only set one type of discount per line."
        ):
            self.contract4.contract_line_ids.discount = 42

    def test_price_subtotal_discount_percent(self):
        self.assertEqual(self.contract.contract_line_ids.price_subtotal, 50.0)

    def test_price_subtotal_discount_fixed(self):
        self.assertEqual(self.contract4.contract_line_ids.price_subtotal, 52.0)
