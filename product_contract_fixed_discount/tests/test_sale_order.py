# Copyright 2023 Foodles
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.product_contract.tests.common import CommonProductContractSaleOrderCase


class TestSaleOrder(CommonProductContractSaleOrderCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order_line1.discount_fixed = 11.0
        cls.contract_template2.contract_line_ids.discount = 0
        cls.contract_template2.contract_line_ids.discount_fixed = 50
        cls.order_line2.product_id_change()
        cls.order_line2.discount_fixed = 22.0

    def test_action_confirm(self):
        """It should create a contract for each contract template used in
        order_line with propagated fixed_discount"""
        self.order_line1._compute_auto_renew()
        self.sale.action_confirm()
        contracts = self.sale.order_line.mapped("contract_id")
        self.assertEqual(len(contracts), 2)
        contract_line = self.order_line1.contract_id.contract_line_ids
        self.assertEqual(contract_line.discount_fixed, 11)
        self.assertEqual(contract_line.discount_fixed, 11)
        self.assertEqual(
            sorted(
                self.order_line2.contract_id.contract_line_ids.mapped("discount_fixed")
            ),
            sorted([50, 22]),
        )
