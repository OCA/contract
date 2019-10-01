# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.product_contract.tests.test_sale_order import TestSaleOrder


class TestSaleOrderPaymentMode(TestSaleOrder):
    def setUp(self):
        super(TestSaleOrderPaymentMode, self).setUp()
        self.payment_mode = self.env['account.payment.mode'].search(
            [], limit=1
        )
        self.sale.payment_mode_id = self.payment_mode

    def test_action_confirm_with_payment_mode(self):
        self.test_action_confirm()
        self.assertEqual(
            self.sale.order_line.mapped('contract_id.payment_mode_id'),
            self.payment_mode,
        )
