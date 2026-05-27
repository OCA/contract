# Copyright 2026 Domatix - Alvaro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.product.tests.common import ProductCommon


class TestSubscriptionMRR(ProductCommon, BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.pricelist = cls.env["product.pricelist"].create({"name": "MRR pricelist"})
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "MRR test partner",
                "property_product_pricelist": cls.pricelist.id,
            }
        )
        cls.product = cls._create_product(
            name="MRR product",
            lst_price=120.0,
            subscribable=True,
            uom_id=cls.uom_unit.id,
            taxes_id=[(6, 0, [])],
        )
        cls.stage_draft = cls.env["sale.subscription.stage"].search(
            [("type", "=", "draft")], limit=1
        )

    @classmethod
    def _create_template(cls, rule_type, interval=1):
        return cls.env["sale.subscription.template"].create(
            {
                "name": f"Tmpl {rule_type} {interval}",
                "code": f"T{rule_type[0].upper()}{interval}",
                "recurring_rule_type": rule_type,
                "recurring_interval": interval,
            }
        )

    def _create_subscription(self, template, price_unit=120.0, qty=1.0):
        subscription = self.env["sale.subscription"].create(
            {
                "partner_id": self.partner.id,
                "template_id": template.id,
                "pricelist_id": self.pricelist.id,
                "stage_id": self.stage_draft.id,
            }
        )
        self.env["sale.subscription.line"].create(
            {
                "sale_subscription_id": subscription.id,
                "product_id": self.product.id,
                "product_uom_qty": qty,
                "price_unit": price_unit,
                "tax_ids": [(6, 0, [])],
            }
        )
        return subscription

    def test_mrr_monthly_template_equals_subtotal(self):
        tmpl = self._create_template("months", 1)
        sub = self._create_subscription(tmpl, price_unit=120.0)
        self.assertAlmostEqual(sub.recurring_monthly, sub.recurring_total, 2)

    def test_mrr_yearly_template_is_one_twelfth(self):
        tmpl = self._create_template("years", 1)
        sub = self._create_subscription(tmpl, price_unit=1200.0)
        self.assertAlmostEqual(sub.recurring_monthly, 100.0, 2)

    def test_mrr_weekly_template_uses_factor(self):
        # 1 week == 7/30.4375 months, so MRR = subtotal / (7/30.4375)
        tmpl = self._create_template("weeks", 1)
        sub = self._create_subscription(tmpl, price_unit=100.0)
        self.assertAlmostEqual(sub.recurring_monthly, 100.0 * 30.4375 / 7, 2)

    def test_mrr_daily_template_uses_factor(self):
        # 1 day == 1/30.4375 months, so MRR = subtotal * 30.4375
        tmpl = self._create_template("days", 1)
        sub = self._create_subscription(tmpl, price_unit=10.0)
        self.assertAlmostEqual(sub.recurring_monthly, 10.0 * 30.4375, 2)

    def test_mrr_respects_recurring_interval(self):
        # 3-month interval at 300 -> MRR == 100
        tmpl = self._create_template("months", 3)
        sub = self._create_subscription(tmpl, price_unit=300.0)
        self.assertAlmostEqual(sub.recurring_monthly, 100.0, 2)

    def test_mrr_aggregates_over_lines(self):
        tmpl = self._create_template("months", 1)
        sub = self._create_subscription(tmpl, price_unit=120.0)
        self.env["sale.subscription.line"].create(
            {
                "sale_subscription_id": sub.id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "price_unit": 80.0,
                "tax_ids": [(6, 0, [])],
            }
        )
        self.assertAlmostEqual(sub.recurring_monthly, 200.0, 2)

    def test_arr_is_12x_mrr(self):
        tmpl = self._create_template("months", 1)
        sub = self._create_subscription(tmpl, price_unit=150.0)
        self.assertAlmostEqual(sub.recurring_yearly, sub.recurring_monthly * 12, 2)

    def test_mrr_recomputes_after_qty_change(self):
        tmpl = self._create_template("months", 1)
        sub = self._create_subscription(tmpl, price_unit=100.0, qty=1.0)
        line = sub.sale_subscription_line_ids
        self.assertAlmostEqual(sub.recurring_monthly, 100.0, 2)
        line.product_uom_qty = 3.0
        self.assertAlmostEqual(sub.recurring_monthly, 300.0, 2)

    def test_mrr_recomputes_after_template_recurrence_change(self):
        tmpl_monthly = self._create_template("months", 1)
        tmpl_yearly = self._create_template("years", 1)
        sub = self._create_subscription(tmpl_monthly, price_unit=1200.0)
        self.assertAlmostEqual(sub.recurring_monthly, 1200.0, 2)
        sub.template_id = tmpl_yearly
        self.assertAlmostEqual(sub.recurring_monthly, 100.0, 2)
