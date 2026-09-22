# Copyright 2026 Domatix - Alvaro Domatix
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import UserError
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.product.tests.common import ProductCommon


class TestSubscriptionDuplicateInvoices(ProductCommon, BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "Dup partner"})
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Dup pricelist"})
        cls.template = cls.env["sale.subscription.template"].create(
            {
                "name": "Dup template",
                "code": "DUP-MTH",
                "recurring_rule_type": "months",
                "recurring_rule_boundary": "unlimited",
                "invoicing_mode": "draft",
            }
        )
        cls.product = cls._create_product(
            name="Dup product",
            lst_price=50.0,
            subscribable=True,
            uom_id=cls.uom_unit.id,
        )

    def _make_subscription(self):
        sub = self.env["sale.subscription"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "template_id": self.template.id,
                "date_start": fields.Date.today(),
                "recurring_next_date": fields.Date.today(),
            }
        )
        self.env["sale.subscription.line"].create(
            {
                "sale_subscription_id": sub.id,
                "product_id": self.product.id,
            }
        )
        return sub

    def _rewind_to_invoiced_period(self, sub, period_start):
        """Put ``recurring_next_date`` back to the period that was just billed.

        This reproduces the real situation the guard protects against: a run
        created (and committed) the invoice for that period but was interrupted
        before advancing ``recurring_next_date`` (e.g. the cron crashed, or the
        email step failed after the invoice was posted). On the next run the
        subscription is still due for the *same* period and must not be billed
        twice.
        """
        sub.recurring_next_date = period_start

    def test_draft_invoice_blocks_duplicate(self):
        sub = self._make_subscription()
        period_start = sub.recurring_next_date
        sub.manual_invoice()
        self._rewind_to_invoiced_period(sub, period_start)
        with self.assertRaises(UserError):
            sub.manual_invoice()

    def test_posted_invoice_blocks_duplicate(self):
        sub = self._make_subscription()
        period_start = sub.recurring_next_date
        invoice = sub.create_invoice()
        invoice.action_post()
        self._rewind_to_invoiced_period(sub, period_start)
        with self.assertRaises(UserError):
            sub.manual_invoice()

    def test_next_period_is_not_blocked(self):
        # After a normal invoice the date advances to the next period, which is
        # a different (not-yet-billed) period and must be allowed.
        sub = self._make_subscription()
        sub.manual_invoice()
        period_start, period_end = sub._get_invoice_period()
        self.assertTrue(sub._can_create_invoice_for_period(period_start, period_end))
        invoice = sub.manual_invoice()
        self.assertTrue(invoice)

    def test_cancelled_invoice_does_not_block(self):
        sub = self._make_subscription()
        period_start = sub.recurring_next_date
        invoice = sub.create_invoice()
        invoice.button_cancel()
        self._rewind_to_invoiced_period(sub, period_start)
        period_start, period_end = sub._get_invoice_period()
        self.assertTrue(sub._can_create_invoice_for_period(period_start, period_end))

    def test_can_create_invoice_for_fresh_period(self):
        sub = self._make_subscription()
        period_start, period_end = sub._get_invoice_period()
        self.assertTrue(sub._can_create_invoice_for_period(period_start, period_end))

    def test_user_error_message_contains_period(self):
        sub = self._make_subscription()
        period_start = sub.recurring_next_date
        sub.manual_invoice()
        self._rewind_to_invoiced_period(sub, period_start)
        with self.assertRaises(UserError) as ctx:
            sub.manual_invoice()
        self.assertIn("already exists", str(ctx.exception))

    def test_generate_invoice_skips_duplicate(self):
        sub = self._make_subscription()
        period_start = sub.recurring_next_date
        sub.manual_invoice()
        invoices_before = self.env["account.move"].search_count(
            [("subscription_id", "=", sub.id)]
        )
        self._rewind_to_invoiced_period(sub, period_start)
        with mute_logger("odoo.addons.subscription_oca.models.sale_subscription"):
            result = sub.generate_invoice()
        self.assertFalse(result)
        invoices_after = self.env["account.move"].search_count(
            [("subscription_id", "=", sub.id)]
        )
        self.assertEqual(invoices_before, invoices_after)
