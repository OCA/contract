# Copyright 2026 Domatix - Alvaro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.product.tests.common import ProductCommon


class TestSubscriptionPause(ProductCommon, BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Pause pl"})
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Pause partner",
                "property_product_pricelist": cls.pricelist.id,
            }
        )
        cls.product = cls._create_product(
            name="Pause product",
            lst_price=100.0,
            subscribable=True,
            uom_id=cls.uom_unit.id,
            taxes_id=[(6, 0, [])],
        )
        cls.template = cls.env["sale.subscription.template"].create(
            {
                "name": "Pause template",
                "code": "PAU",
                "recurring_rule_type": "months",
                "recurring_interval": 1,
                "invoicing_mode": "draft",
            }
        )

    def _new_subscription(self, in_progress=True, with_line=True):
        stage = self.env["sale.subscription.stage"].search(
            [("type", "=", "in_progress" if in_progress else "draft")], limit=1
        )
        subscription = self.env["sale.subscription"].create(
            {
                "partner_id": self.partner.id,
                "template_id": self.template.id,
                "pricelist_id": self.pricelist.id,
                "stage_id": stage.id,
                "recurring_next_date": fields.Date.today(),
            }
        )
        if with_line:
            self.env["sale.subscription.line"].create(
                {
                    "sale_subscription_id": subscription.id,
                    "product_id": self.product.id,
                    "product_uom_qty": 1.0,
                    "price_unit": 100.0,
                    "tax_ids": [(6, 0, [])],
                }
            )
        return subscription

    def test_action_pause_sets_flag_and_logs_chatter(self):
        sub = self._new_subscription()
        before = len(sub.message_ids)
        sub.action_pause()
        self.assertTrue(sub.is_paused)
        self.assertFalse(sub.paused_until)
        self.assertGreater(len(sub.message_ids), before)

    def test_action_pause_with_date_stores_paused_until(self):
        sub = self._new_subscription()
        target = fields.Date.today() + relativedelta(days=7)
        sub.action_pause(paused_until=target)
        self.assertTrue(sub.is_paused)
        self.assertEqual(sub.paused_until, target)

    def test_action_pause_on_closed_raises(self):
        sub = self._new_subscription()
        sub.close_subscription()
        with self.assertRaises(UserError):
            sub.action_pause()

    def test_action_pause_when_already_paused_raises(self):
        sub = self._new_subscription()
        sub.action_pause()
        with self.assertRaises(UserError):
            sub.action_pause()

    def test_action_resume_clears_flag(self):
        sub = self._new_subscription()
        sub.action_pause(paused_until=fields.Date.today() + relativedelta(days=3))
        sub.action_resume()
        self.assertFalse(sub.is_paused)
        self.assertFalse(sub.paused_until)

    def test_action_resume_when_not_paused_raises(self):
        sub = self._new_subscription()
        with self.assertRaises(UserError):
            sub.action_resume()

    def test_cron_does_not_invoice_paused(self):
        sub = self._new_subscription()
        sub.in_progress = True
        sub.recurring_next_date = fields.Date.today() - relativedelta(days=1)
        sub.action_pause()
        invoices_before = self.env["account.move"].search_count(
            [("subscription_id", "=", sub.id)]
        )
        sub.cron_subscription_management()
        invoices_after = self.env["account.move"].search_count(
            [("subscription_id", "=", sub.id)]
        )
        self.assertEqual(invoices_after, invoices_before)
        self.assertTrue(sub.is_paused)

    def test_cron_resumes_when_paused_until_past(self):
        sub = self._new_subscription()
        sub.action_pause(paused_until=fields.Date.today() - relativedelta(days=1))
        sub._cron_resume_due_subscriptions()
        self.assertFalse(sub.is_paused)
        self.assertFalse(sub.paused_until)

    def test_cron_keeps_paused_when_paused_until_future(self):
        sub = self._new_subscription()
        future = fields.Date.today() + relativedelta(days=30)
        sub.action_pause(paused_until=future)
        sub._cron_resume_due_subscriptions()
        self.assertTrue(sub.is_paused)
        self.assertEqual(sub.paused_until, future)

    def test_cron_keeps_paused_when_no_paused_until(self):
        sub = self._new_subscription()
        sub.action_pause()
        sub._cron_resume_due_subscriptions()
        self.assertTrue(sub.is_paused)
        self.assertFalse(sub.paused_until)

    def test_cron_invoices_active_not_paused(self):
        # Control for test_cron_does_not_invoice_paused: the same due
        # subscription, when NOT paused, must actually be invoiced.
        sub = self._new_subscription()
        sub.in_progress = True
        sub.recurring_next_date = fields.Date.today() - relativedelta(days=1)
        invoices_before = self.env["account.move"].search_count(
            [("subscription_id", "=", sub.id)]
        )
        sub.cron_subscription_management()
        invoices_after = self.env["account.move"].search_count(
            [("subscription_id", "=", sub.id)]
        )
        self.assertGreater(invoices_after, invoices_before)

    def test_pause_wizard_schedules_resume(self):
        # The wizard is the only UI path that can set paused_until.
        sub = self._new_subscription()
        target = fields.Date.today() + relativedelta(days=14)
        wizard = (
            self.env["sale.subscription.pause.wizard"]
            .with_context(active_id=sub.id)
            .create({"paused_until": target})
        )
        wizard.button_confirm()
        self.assertTrue(sub.is_paused)
        self.assertEqual(sub.paused_until, target)

    def test_action_open_pause_wizard_returns_action(self):
        sub = self._new_subscription()
        action = sub.action_open_pause_wizard()
        self.assertEqual(action["res_model"], "sale.subscription.pause.wizard")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "new")

    @mute_logger("odoo.addons.subscription_oca.models.sale_subscription")
    def test_cron_resume_logs_error_when_resume_fails(self):
        # A failing resume must be swallowed by the cron (logged) and leave
        # the subscription paused, so one bad record cannot break the batch.
        sub = self._new_subscription()
        sub.action_pause(paused_until=fields.Date.today() - relativedelta(days=1))
        with patch.object(
            type(self.env["sale.subscription"]),
            "action_resume",
            side_effect=ValueError("boom"),
        ):
            self.env["sale.subscription"]._cron_resume_due_subscriptions()
        self.assertTrue(sub.is_paused)
