# Copyright 2026 Domatix
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from .test_subscription_oca import TestSubscriptionOCA


class TestSubscriptionInvoicingOptions(TestSubscriptionOCA):
    """Cover the orthogonal invoicing options that replaced ``invoicing_mode``.

    The three template fields (``create_sale_order``, ``invoice_state`` and
    ``send_invoice``) must be independent of each other, so the behaviour is
    tested as a matrix rather than a single mode selector.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Invoice on order confirmation so the sale-order path is invoiceable.
        (cls.product_1 | cls.product_2).write({"invoice_policy": "order"})

    def _make_subscription(self, template_vals):
        template = self.create_sub_template(template_vals)
        subscription = self.create_sub(
            {
                "template_id": template.id,
                "date_start": fields.Date.today(),
                "recurring_next_date": fields.Date.today(),
                "journal_id": self.sale_journal.id,
                "in_progress": True,
            }
        )
        self.create_sub_line(subscription)
        return subscription

    def test_draft_invoice_without_sale_order(self):
        subscription = self._make_subscription(
            {"create_sale_order": False, "invoice_state": "draft"}
        )
        subscription.generate_invoice()
        self.assertFalse(subscription.sale_order_ids)
        self.assertEqual(len(subscription.invoice_ids), 1)
        self.assertEqual(subscription.invoice_ids.state, "draft")

    def test_posted_invoice_not_sent(self):
        subscription = self._make_subscription(
            {
                "create_sale_order": False,
                "invoice_state": "posted",
                "send_invoice": False,
            }
        )
        subscription.generate_invoice()
        invoice = subscription.invoice_ids
        self.assertEqual(invoice.state, "posted")
        self.assertFalse(invoice.is_move_sent)

    def test_posted_invoice_sent(self):
        subscription = self._make_subscription(
            {
                "create_sale_order": False,
                "invoice_state": "posted",
                "send_invoice": True,
                "invoice_mail_template_id": self.env.ref(
                    "account.email_template_edi_invoice"
                ).id,
            }
        )
        subscription.generate_invoice()
        invoice = subscription.invoice_ids
        self.assertEqual(invoice.state, "posted")
        self.assertTrue(invoice.is_move_sent)

    def test_sale_order_with_posted_invoice(self):
        subscription = self._make_subscription(
            {
                "create_sale_order": True,
                "invoice_state": "posted",
                "send_invoice": False,
            }
        )
        subscription.generate_invoice()
        order = subscription.sale_order_ids
        self.assertTrue(order)
        self.assertEqual(order.state, "sale")
        invoice = order.invoice_ids
        self.assertEqual(invoice.state, "posted")
        self.assertIn(order.name, invoice.invoice_origin)
        self.assertIn(subscription.name, invoice.invoice_origin)

    def test_sale_order_with_draft_invoice(self):
        # The axes are independent: a sale order can be generated while the
        # invoice is still left in draft (impossible with the old selector).
        subscription = self._make_subscription(
            {
                "create_sale_order": True,
                "invoice_state": "draft",
                "send_invoice": False,
            }
        )
        subscription.generate_invoice()
        order = subscription.sale_order_ids
        self.assertTrue(order)
        invoice = order.invoice_ids
        self.assertEqual(invoice.state, "draft")
