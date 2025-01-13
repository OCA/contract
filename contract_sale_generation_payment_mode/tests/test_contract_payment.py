from odoo.tests.common import TransactionCase

from odoo.addons.contract_sale_generation.tests.common import ContractSaleCommon


class TestContractSaleGenerationPaymentMode(ContractSaleCommon, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payment_method = cls.env["account.payment.method"].create(
            {
                "name": "Test Payment Method",
                "code": "Test",
                "payment_type": "inbound",
            }
        )

        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test payment mode",
                "active": True,
                "payment_method_id": cls.payment_method.id,
                "bank_account_link": "variable",
            }
        )

        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Test",
                "partner_id": cls.partner.id,
                "payment_mode_id": cls.payment_mode.id,
                "line_recurrence": True,
                "contract_type": "sale",
                "recurring_interval": 1,
                "recurring_rule_type": "monthly",
                "date_start": "2018-01-15",
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_1.id,
                            "name": "Database Administration 25",
                            "quantity": 2.0,
                            "uom_id": cls.product_1.uom_id.id,
                            "price_unit": 200.0,
                        },
                    )
                ],
            }
        )

    def test_contract_sale_generation_with_payment_mode(self):
        order = self.contract.recurring_create_sale()[0]
        self.assertEqual(self.payment_mode, order.payment_mode_id)

    def test_contract_sale_generation_without_payment_mode(self):
        self.contract.payment_mode_id = False
        order = self.contract.recurring_create_sale()[0]
        self.assertFalse(self.contract.payment_mode_id)
        self.assertFalse(order.payment_mode_id)

    def test_contract_sale_generation_generation_no_contract_line(self):
        self.contract.contract_line_ids.cancel()
        self.contract.contract_line_ids = False
        order = self.contract.recurring_create_sale()
        self.assertFalse(order)
