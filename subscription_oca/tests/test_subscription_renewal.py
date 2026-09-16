# Copyright 2026 Domatix - Alvaro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.product.tests.common import ProductCommon


class TestSubscriptionRenewal(ProductCommon, BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Renewal pl"})
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Renewal partner",
                "property_product_pricelist": cls.pricelist.id,
            }
        )
        cls.product = cls._create_product(
            name="Renewal product",
            lst_price=100.0,
            subscribable=True,
            uom_id=cls.uom_unit.id,
            taxes_id=[(6, 0, [])],
        )
        cls.template = cls.env["sale.subscription.template"].create(
            {
                "name": "Renewal template",
                "code": "RNW",
                "recurring_rule_type": "months",
                "recurring_interval": 1,
            }
        )
        cls.stage_pre = cls.env["sale.subscription.stage"].search(
            [("type", "=", "pre")], limit=1
        )
        cls.stage_in_progress = cls.env["sale.subscription.stage"].search(
            [("type", "=", "in_progress")], limit=1
        )
        cls.stage_post = cls.env["sale.subscription.stage"].search(
            [("type", "=", "post")], limit=1
        )

    def _new_subscription(self, with_line=True):
        subscription = self.env["sale.subscription"].create(
            {
                "partner_id": self.partner.id,
                "template_id": self.template.id,
                "pricelist_id": self.pricelist.id,
                "stage_id": self.stage_in_progress.id,
            }
        )
        if with_line:
            self.env["sale.subscription.line"].create(
                {
                    "sale_subscription_id": subscription.id,
                    "product_id": self.product.id,
                    "product_uom_qty": 2.0,
                    "price_unit": 50.0,
                    "tax_ids": [(6, 0, [])],
                }
            )
        return subscription

    def test_prepare_renewal_creates_child_in_pre_stage(self):
        parent = self._new_subscription()
        action = parent.action_prepare_renewal()
        child = self.env["sale.subscription"].browse(action["res_id"])
        self.assertTrue(child.exists())
        self.assertEqual(child.parent_subscription_id, parent)
        self.assertEqual(child.stage_id.type, "pre")

    def test_renewal_inherits_lines(self):
        parent = self._new_subscription()
        parent.action_prepare_renewal()
        child = parent.child_subscription_ids
        self.assertEqual(len(child.sale_subscription_line_ids), 1)
        line = child.sale_subscription_line_ids
        self.assertEqual(line.product_id, self.product)
        self.assertEqual(line.product_uom_qty, 2.0)

    def test_renewal_inherits_template_pricelist_fiscal(self):
        parent = self._new_subscription()
        parent.action_prepare_renewal()
        child = parent.child_subscription_ids
        self.assertEqual(child.template_id, parent.template_id)
        self.assertEqual(child.pricelist_id, parent.pricelist_id)
        self.assertEqual(child.fiscal_position_id, parent.fiscal_position_id)
        self.assertEqual(child.partner_id, parent.partner_id)

    def test_renewal_date_start_uses_parent_finish_date(self):
        parent = self._new_subscription()
        # Distinct values so the assert actually exercises the finish-date path.
        parent.date = date(2026, 12, 31)
        parent.recurring_next_date = date(2026, 1, 1)
        parent.action_prepare_renewal()
        self.assertEqual(parent.child_subscription_ids.date_start, date(2026, 12, 31))

    def test_renewal_date_start_falls_back_to_next_invoice_date(self):
        parent = self._new_subscription()
        parent.date = False
        parent.recurring_next_date = date(2026, 1, 1)
        parent.action_prepare_renewal()
        self.assertEqual(parent.child_subscription_ids.date_start, date(2026, 1, 1))

    def test_renewal_start_closes_parent(self):
        parent = self._new_subscription()
        parent.action_prepare_renewal()
        child = parent.child_subscription_ids
        child.action_start_subscription()
        self.assertEqual(parent.stage_id.type, "post")

    def test_origin_walks_chain(self):
        first = self._new_subscription()
        first.action_prepare_renewal()
        second = first.child_subscription_ids
        second.action_prepare_renewal()
        third = second.child_subscription_ids
        self.assertEqual(third.origin_subscription_id, first)
        self.assertEqual(second.origin_subscription_id, first)
        self.assertFalse(first.origin_subscription_id)

    def test_is_renewed_when_child_active(self):
        parent = self._new_subscription()
        parent.action_prepare_renewal()
        self.assertTrue(parent.is_renewed)

    def test_is_renewed_false_when_only_closed_child(self):
        parent = self._new_subscription()
        parent.action_prepare_renewal()
        child = parent.child_subscription_ids
        child.close_subscription()
        # Closing the child must recompute the stored field automatically.
        self.assertFalse(parent.is_renewed)

    def test_cannot_renew_closed_subscription(self):
        subscription = self._new_subscription()
        subscription.close_subscription()
        with self.assertRaises(UserError):
            subscription.action_prepare_renewal()

    def test_cannot_renew_when_active_child_exists(self):
        parent = self._new_subscription()
        parent.action_prepare_renewal()
        with self.assertRaises(UserError):
            parent.action_prepare_renewal()

    def test_chatter_message_on_renewal_creation(self):
        parent = self._new_subscription()
        parent.action_prepare_renewal()
        child = parent.child_subscription_ids
        # The latest message links to the freshly created renewal.
        body = parent.message_ids[0].body
        self.assertIn("Renewal", body)
        self.assertIn(str(child.id), body)

    def test_renewal_count_reflects_children(self):
        parent = self._new_subscription()
        self.assertEqual(parent.renewal_count, 0)
        parent.action_prepare_renewal()
        self.assertEqual(parent.renewal_count, 1)

    def test_renewal_activation_skips_already_closed_parent(self):
        # If the parent is already closed when its renewal is activated,
        # the activation hook is a no-op: it must not re-close the parent
        # nor post a "renewal activated" note.
        parent = self._new_subscription()
        parent.action_prepare_renewal()
        child = parent.child_subscription_ids
        parent.close_subscription()
        messages_before = parent.message_ids
        child.action_start_subscription()
        self.assertEqual(parent.stage_id.type, "post")
        self.assertEqual(parent.message_ids, messages_before)

    def test_renewal_date_start_falls_back_to_today(self):
        parent = self._new_subscription()
        parent.date = False
        parent.recurring_next_date = False
        parent.action_prepare_renewal()
        self.assertEqual(parent.child_subscription_ids.date_start, date.today())

    def test_action_view_parent_and_children(self):
        parent = self._new_subscription()
        parent.action_prepare_renewal()
        child = parent.child_subscription_ids
        parent_action = child.action_view_parent_subscription()
        self.assertEqual(parent_action["res_model"], "sale.subscription")
        self.assertEqual(parent_action["res_id"], parent.id)
        children_action = parent.action_view_child_subscriptions()
        self.assertEqual(children_action["res_model"], "sale.subscription")
        self.assertEqual(children_action["domain"], [("id", "in", child.ids)])
