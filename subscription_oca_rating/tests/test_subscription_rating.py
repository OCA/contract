# Copyright 2026 Domatix - Alvaro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.subscription_oca_rating.models.sale_subscription import (
    RATING_TEMPLATE,
)


class TestSubscriptionRating(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Rating PL"})
        cls.partner = cls.env["res.partner"].create(
            {"name": "Rating partner", "email": "rating@example.com"}
        )
        cls.template = cls.env["sale.subscription.template"].create(
            {
                "name": "Rating tmpl",
                "code": "R",
                "recurring_rule_type": "months",
            }
        )
        cls.stage = cls.env["sale.subscription.stage"].search(
            [("type", "=", "in_progress")], limit=1
        )
        cls.subscription = cls.env["sale.subscription"].create(
            {
                "partner_id": cls.partner.id,
                "template_id": cls.template.id,
                "pricelist_id": cls.pricelist.id,
                "stage_id": cls.stage.id,
            }
        )

    def _create_consumed_rating(self, value):
        return self.env["rating.rating"].create(
            {
                "res_model": "sale.subscription",
                "res_id": self.subscription.id,
                "res_model_id": self.env["ir.model"]._get_id("sale.subscription"),
                "rating": value,
                "consumed": True,
                "partner_id": self.partner.id,
            }
        )

    def test_initial_rating_count_is_zero(self):
        self.assertEqual(self.subscription.rating_count, 0)

    def test_rating_count_reflects_consumed_ratings(self):
        self._create_consumed_rating(5)
        self.subscription.invalidate_recordset(["rating_count", "rating_avg"])
        self.assertEqual(self.subscription.rating_count, 1)
        self.assertEqual(self.subscription.rating_avg, 5.0)

    def test_rating_avg_computes_over_multiple(self):
        self._create_consumed_rating(5)
        self._create_consumed_rating(1)
        self.subscription.invalidate_recordset(["rating_count", "rating_avg"])
        self.assertEqual(self.subscription.rating_count, 2)
        self.assertEqual(self.subscription.rating_avg, 3.0)

    def test_send_rating_request_creates_pending_rating(self):
        self.assertFalse(self.subscription.rating_ids)
        self.assertTrue(self.subscription.action_send_rating_request())
        rating = self.subscription.rating_ids
        self.assertEqual(len(rating), 1)
        self.assertFalse(rating.consumed)
        self.assertEqual(rating.partner_id, self.partner)
        self.assertEqual(rating.rated_partner_id, self.subscription.user_id.partner_id)
        self.assertTrue(rating.access_token)

    def test_send_rating_request_reuses_pending_token(self):
        self.subscription.action_send_rating_request()
        token = self.subscription.rating_ids.access_token
        self.subscription.action_send_rating_request()
        pending = self.subscription.rating_ids.filtered(lambda r: not r.consumed)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending.access_token, token)

    def test_closing_subscription_sends_rating_request(self):
        self.assertFalse(self.subscription.rating_ids)
        self.subscription.close_subscription()
        rating = self.subscription.rating_ids
        self.assertEqual(len(rating), 1)
        self.assertFalse(rating.consumed)
        self.assertEqual(self.subscription.stage_id.type, "post")

    def test_closing_without_partner_email_skips_rating(self):
        self.partner.email = False
        self.subscription.close_subscription()
        self.assertFalse(self.subscription.rating_ids)

    def test_send_rating_request_without_template_returns_false(self):
        self.env.ref(RATING_TEMPLATE).unlink()
        self.assertFalse(self.subscription.action_send_rating_request())
        self.assertFalse(self.subscription.rating_ids)

    def test_closing_without_template_still_closes(self):
        self.env.ref(RATING_TEMPLATE).unlink()
        self.subscription.close_subscription()
        self.assertEqual(self.subscription.stage_id.type, "post")
        self.assertFalse(self.subscription.rating_ids)

    @mute_logger("odoo.addons.subscription_oca_rating.models.sale_subscription")
    def test_closing_survives_rating_send_failure(self):
        with patch.object(
            type(self.subscription),
            "rating_send_request",
            side_effect=Exception("SMTP down"),
        ):
            self.subscription.close_subscription()
        self.assertEqual(self.subscription.stage_id.type, "post")
