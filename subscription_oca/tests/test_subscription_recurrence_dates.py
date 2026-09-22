# Copyright 2026 Domatix - Alvaro Domatix
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.product.tests.common import ProductCommon


class TestSubscriptionRecurrenceDates(ProductCommon, BaseCommon):
    """Recurrence date arithmetic for sale.subscription.

    Assertions use hand-computed fixed calendar values (never a
    ``relativedelta`` rebuilt from the model fields), so a test failing means
    the produced date is wrong, not that the formula was merely re-typed.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "Recurrence partner"})
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Recurrence pricelist"}
        )
        cls.product = cls._create_product(
            name="Recurrence product",
            lst_price=100.0,
            subscribable=True,
            uom_id=cls.uom_unit.id,
        )

    @classmethod
    def _make_template(cls, rule_type, boundary="unlimited", count=1, interval=1):
        return cls.env["sale.subscription.template"].create(
            {
                "name": f"Tmpl {rule_type} {boundary} i{interval} c{count}",
                "code": f"REC-{rule_type}-{boundary}-{interval}-{count}",
                "recurring_rule_type": rule_type,
                "recurring_rule_boundary": boundary,
                "recurring_rule_count": count,
                "recurring_interval": interval,
            }
        )

    def _make_subscription(self, template, date_start=None):
        return self.env["sale.subscription"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "template_id": template.id,
                "date_start": date_start or date(2026, 1, 1),
            }
        )

    # ------------------------------------------------------------------
    # Contract end date (field `date`, computed by `_compute_rule_boundary`,
    # production path used by the auto-close cron) and its helper.
    # ------------------------------------------------------------------

    def test_contract_end_unlimited_has_no_finish_date(self):
        sub = self._make_subscription(self._make_template("months", "unlimited"))
        self.assertFalse(sub.date)
        self.assertTrue(sub.recurring_rule_boundary)
        self.assertFalse(sub._get_contract_end_date())

    def test_contract_end_monthly(self):
        # Gym membership: 1 month, billed monthly.
        sub = self._make_subscription(
            self._make_template("months", "limited", count=1),
            date_start=date(2026, 1, 1),
        )
        self.assertEqual(sub.date, date(2026, 2, 1))

    def test_contract_end_weekly_limited_is_weeks_not_months(self):
        # Fruit box: 4 weekly deliveries. End must be 28 days later
        # (2026-01-29), NOT 4 months later. This case failed before the fix
        # that made the contract end honor recurring_rule_type.
        sub = self._make_subscription(
            self._make_template("weeks", "limited", count=4),
            date_start=date(2026, 1, 1),
        )
        self.assertEqual(sub.date, date(2026, 1, 29))

    def test_contract_end_quarterly_honors_interval_times_count(self):
        # Billed every 3 months, for 2 periods => 6 months total.
        sub = self._make_subscription(
            self._make_template("months", "limited", count=2, interval=3),
            date_start=date(2026, 1, 1),
        )
        self.assertEqual(sub.date, date(2026, 7, 1))

    def test_contract_end_yearly(self):
        sub = self._make_subscription(
            self._make_template("years", "limited", count=1),
            date_start=date(2026, 1, 1),
        )
        self.assertEqual(sub.date, date(2027, 1, 1))

    def test_contract_end_field_and_helper_agree(self):
        # The stored `date` field and `_get_contract_end_date()` must stay
        # coherent when date_start is set (the normal case).
        for rule_type, count, interval in [
            ("days", 10, 1),
            ("weeks", 4, 1),
            ("months", 2, 3),
            ("years", 1, 1),
        ]:
            template = self._make_template(
                rule_type, "limited", count=count, interval=interval
            )
            sub = self._make_subscription(template, date_start=date(2026, 1, 1))
            self.assertEqual(
                sub.date,
                sub._get_contract_end_date(),
                f"Mismatch for {rule_type} count={count} interval={interval}",
            )

    # ------------------------------------------------------------------
    # One billing period (`_get_recurrence_delta` via `_get_next_invoice_date`).
    # The period uses interval but NOT rule_count.
    # ------------------------------------------------------------------

    def test_next_invoice_date_monthly(self):
        sub = self._make_subscription(self._make_template("months"))
        self.assertEqual(sub._get_next_invoice_date(date(2026, 1, 1)), date(2026, 2, 1))

    def test_next_invoice_date_weekly(self):
        sub = self._make_subscription(self._make_template("weeks"))
        self.assertEqual(sub._get_next_invoice_date(date(2026, 1, 1)), date(2026, 1, 8))

    def test_next_invoice_date_honors_interval(self):
        # Quarterly: one period is 3 months ahead.
        sub = self._make_subscription(self._make_template("months", interval=3))
        self.assertEqual(sub._get_next_invoice_date(date(2026, 1, 1)), date(2026, 4, 1))

    def test_period_ignores_rule_count_while_end_uses_it(self):
        # A 12-month limited subscription: one billing period is still a
        # single month, but the contract ends after 12. This distinguishes
        # `_get_recurrence_delta` (period) from `_get_date` (total span).
        template = self._make_template("months", "limited", count=12)
        sub = self._make_subscription(template, date_start=date(2026, 1, 1))
        self.assertEqual(sub._get_next_invoice_date(date(2026, 1, 1)), date(2026, 2, 1))
        self.assertEqual(sub.date, date(2027, 1, 1))

    # ------------------------------------------------------------------
    # First invoice date and post-invoice advance.
    # ------------------------------------------------------------------

    def test_first_invoice_date_uses_date_start(self):
        sub = self._make_subscription(
            self._make_template("months"), date_start=date(2026, 3, 15)
        )
        self.assertEqual(sub._get_first_invoice_date(), date(2026, 3, 15))

    def test_set_next_invoice_date_after_invoice_advances_one_period(self):
        sub = self._make_subscription(self._make_template("weeks"))
        sub.recurring_next_date = date(2026, 1, 1)
        sub._set_next_invoice_date_after_invoice()
        self.assertEqual(sub.recurring_next_date, date(2026, 1, 8))

    # ------------------------------------------------------------------
    # Integration: generating an invoice advances recurring_next_date by
    # exactly one period (production path, not just the helper in isolation).
    # ------------------------------------------------------------------

    def test_generate_invoice_advances_recurring_next_date(self):
        template = self._make_template("months")  # invoice_state defaults to draft
        sub = self._make_subscription(template, date_start=date(2026, 1, 1))
        sub.recurring_next_date = date(2026, 1, 1)
        self.env["sale.subscription.line"].create(
            {
                "sale_subscription_id": sub.id,
                "product_id": self.product.id,
                "company_id": sub.company_id.id,
            }
        )
        sub.generate_invoice()
        self.assertTrue(sub.invoice_ids, "generate_invoice should create a draft move")
        self.assertEqual(sub.recurring_next_date, date(2026, 2, 1))

    def test_rule_boundary_without_template(self):
        # A new record in the form view computes the boundary before any
        # template is selected: it must not crash and must have no end date.
        subscription = self.env["sale.subscription"].new({})
        self.assertFalse(subscription.date)
        self.assertTrue(subscription.recurring_rule_boundary)

    def test_set_next_invoice_date_without_previous_date(self):
        # Manual invoicing of a subscription whose recurring_next_date is
        # empty (e.g. it was closed) must fall back to the first invoice
        # date instead of crashing.
        template = self._make_template("months")
        sub = self._make_subscription(template, date_start=date(2026, 1, 1))
        sub.recurring_next_date = False
        sub._set_next_invoice_date_after_invoice()
        self.assertEqual(sub.recurring_next_date, date(2026, 2, 1))
