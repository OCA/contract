# Copyright 2026 Domatix - Alvaro Domatix
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.product.tests.common import ProductCommon


class TestSubscriptionCron(ProductCommon, BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "Cron partner"})
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Cron pricelist"})
        cls.template = cls.env["sale.subscription.template"].create(
            {
                "name": "Cron template",
                "code": "CRON-MTH",
                "recurring_rule_type": "months",
                "recurring_rule_boundary": "unlimited",
                "invoicing_mode": "draft",
            }
        )
        cls.product = cls._create_product(
            name="Cron product",
            lst_price=10.0,
            subscribable=True,
            uom_id=cls.uom_unit.id,
        )

    def _make_sub(self, **vals):
        defaults = {
            "partner_id": self.partner.id,
            "pricelist_id": self.pricelist.id,
            "template_id": self.template.id,
            "date_start": fields.Date.today(),
        }
        defaults.update(vals)
        sub = self.env["sale.subscription"].create(defaults)
        self.env["sale.subscription.line"].create(
            {
                "sale_subscription_id": sub.id,
                "product_id": self.product.id,
            }
        )
        return sub

    def test_cron_does_not_invoice_future_subscription(self):
        sub = self._make_sub(
            recurring_next_date=fields.Date.today() + relativedelta(days=10),
            in_progress=True,
        )
        self.env["sale.subscription"]._cron_invoice_due_subscriptions()
        self.assertFalse(sub.invoice_ids)

    def test_cron_does_not_invoice_subscription_without_lines(self):
        sub = self.env["sale.subscription"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "template_id": self.template.id,
                "date_start": fields.Date.today(),
                "recurring_next_date": fields.Date.today(),
                "in_progress": True,
            }
        )
        self.env["sale.subscription"]._cron_invoice_due_subscriptions()
        self.assertFalse(sub.invoice_ids)

    def test_cron_invoices_due_subscription(self):
        sub = self._make_sub(
            recurring_next_date=fields.Date.today(),
            in_progress=True,
        )
        self.env["sale.subscription"]._cron_invoice_due_subscriptions()
        self.assertEqual(len(sub.invoice_ids), 1)

    def test_cron_error_on_one_does_not_stop_batch(self):
        sub_ok = self._make_sub(
            recurring_next_date=fields.Date.today(),
            in_progress=True,
        )
        sub_bad = self._make_sub(
            recurring_next_date=fields.Date.today(),
            in_progress=True,
        )
        original_generate = type(sub_ok).generate_invoice
        sub_bad_id = sub_bad.id

        def side_effect(records):
            if records.id == sub_bad_id:
                raise UserError(records.env._("boom"))
            return original_generate(records)

        with patch.object(
            type(sub_ok), "generate_invoice", autospec=True, side_effect=side_effect
        ):
            with mute_logger("odoo.addons.subscription_oca.models.sale_subscription"):
                self.env["sale.subscription"]._cron_invoice_due_subscriptions()

        self.assertEqual(len(sub_ok.invoice_ids), 1)
        self.assertFalse(sub_bad.invoice_ids)

    def test_cron_close_ended_subscription(self):
        template_limited = self.env["sale.subscription.template"].create(
            {
                "name": "Limited template",
                "code": "CRON-LIM",
                "recurring_rule_type": "months",
                "recurring_rule_boundary": "limited",
                "recurring_rule_count": 1,
            }
        )
        sub = self.env["sale.subscription"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "template_id": template_limited.id,
                "date_start": fields.Date.today() - relativedelta(months=2),
                "in_progress": True,
            }
        )
        self.env["sale.subscription"]._cron_close_ended_subscriptions()
        self.assertFalse(sub.in_progress)

    def test_cron_limit_param(self):
        for _ in range(3):
            self._make_sub(
                recurring_next_date=fields.Date.today(),
                in_progress=True,
            )

        def invoiced_count():
            return self.env["sale.subscription"].search_count(
                [
                    ("partner_id", "=", self.partner.id),
                    ("invoice_ids", "!=", False),
                ]
            )

        # limit caps the records handled *per call*: each call with limit=1
        # invoices exactly one more due subscription (the previous one has
        # advanced its next invoice date and is no longer due).
        Subscription = self.env["sale.subscription"]
        Subscription._cron_invoice_due_subscriptions(limit=1)
        self.assertEqual(invoiced_count(), 1)
        Subscription._cron_invoice_due_subscriptions(limit=1)
        self.assertEqual(invoiced_count(), 2)
        Subscription._cron_invoice_due_subscriptions(limit=1)
        self.assertEqual(invoiced_count(), 3)
