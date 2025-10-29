from odoo.addons.payment.tests.common import PaymentCommon


class TestSubscriptionOCARecurrentPayment(PaymentCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pricelist = cls.env.ref("product.list0")
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Subscription Product 1",
                "type": "service",
                "list_price": 100.0,
            }
        )

        cls.account_payment_method = cls.env["account.payment.method"].create(
            {
                "name": "Test Payment Method",
                "code": "none",
                "payment_type": "inbound",
            }
        )

        account_payment_method_line = cls.env["account.payment.method.line"].create(
            {
                "payment_method_id": cls.account_payment_method.id,
                "company_id": cls.company.id,
                "name": "Test Method Line",
            }
        )

        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Test Journal",
                "type": "bank",
                "company_id": cls.company.id,
                "code": "TESTJNL",
                "inbound_payment_method_line_ids": [
                    (4, account_payment_method_line.id)
                ],
            }
        )

        cls.provider_test = cls.dummy_provider.copy(
            {
                "name": "Test Provider for Subscriptions",
                "code": "none",
                "company_id": cls.company.id,
                "journal_id": cls.journal.id,
                "state": "test",
            }
        )

        cls.sub_template = cls.env["sale.subscription.template"].create(
            {
                "name": "Recurring Payment Template",
                "invoicing_mode": "recurring_payment",
                "recurring_interval": 1,
                "recurring_rule_type": "days",
            }
        )

        cls.sub_recurring_payment = cls.env["sale.subscription"].create(
            {
                "name": "Subscription with Recurring Payment",
                "pricelist_id": cls.pricelist.id,
                "partner_id": cls.partner.id,
                "template_id": cls.sub_template.id,
                "date_start": "2025-01-01",
                "recurring_next_date": "2025-01-01",
            }
        )

        cls.line = cls.env["sale.subscription.line"].create(
            {
                "company_id": 1,
                "sale_subscription_id": cls.sub_recurring_payment.id,
                "product_id": cls.product_1.id,
            }
        )

    def test_generate_invoice_recurring_payment(self):
        """Test the generate_invoice method for 'recurring_payment' invoicing mode."""
        subscription = self.sub_recurring_payment
        subscription.generate_invoice()
        self.assertEqual(len(subscription.invoice_ids), 1)
        self._create_token(
            **{"provider_id": self.provider_test.id, "partner_id": self.partner.id}
        )
        subscription.generate_invoice()
        self.assertEqual(len(subscription.invoice_ids), 2)
        last_invoice = subscription.invoice_ids[-1]
        self.assertEqual(last_invoice.state, "posted")
        payments = last_invoice.payment_ids
        self.assertEqual(len(payments), 0)
