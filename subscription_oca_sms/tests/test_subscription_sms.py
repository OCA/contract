# Copyright 2026 Domatix - Alvaro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon

SEND_SMS = "odoo.addons.sms.wizard.sms_composer.SmsComposer.action_send_sms"


class TestSubscriptionSMS(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.pricelist = cls.env["product.pricelist"].create({"name": "SMS PL"})
        cls.partner_with_phone = cls.env["res.partner"].create(
            {"name": "SMS partner", "phone": "+34600000000"}
        )
        cls.partner_no_phone = cls.env["res.partner"].create({"name": "Silent partner"})
        cls.template = cls.env["sale.subscription.template"].create(
            {
                "name": "SMS tmpl",
                "code": "S",
                "recurring_rule_type": "months",
            }
        )
        cls.stage = cls.env["sale.subscription.stage"].search(
            [("type", "=", "in_progress")], limit=1
        )

    def _new_subscription(self, partner=None):
        return self.env["sale.subscription"].create(
            {
                "partner_id": (partner or self.partner_with_phone).id,
                "template_id": self.template.id,
                "pricelist_id": self.pricelist.id,
                "stage_id": self.stage.id,
            }
        )

    # --- data smoke ---------------------------------------------------

    def test_payment_reminder_template_exists(self):
        template = self.env.ref(
            "subscription_oca_sms.sms_template_payment_reminder",
            raise_if_not_found=False,
        )
        self.assertTrue(template)
        self.assertEqual(template.model, "sale.subscription")

    def test_payment_failure_template_exists(self):
        template = self.env.ref(
            "subscription_oca_sms.sms_template_payment_failure",
            raise_if_not_found=False,
        )
        self.assertTrue(template)
        self.assertEqual(template.model, "sale.subscription")

    # --- guard --------------------------------------------------------

    def test_send_sms_raises_when_no_phone(self):
        sub = self._new_subscription(partner=self.partner_no_phone)
        self.assertFalse(sub.can_send_sms)
        with self.assertRaises(UserError):
            sub.action_send_sms_payment_reminder()

    def test_send_sms_raises_when_phone_invalid(self):
        # A non-empty but unparseable number must be rejected by our guard,
        # not slip through to a cryptic error inside the composer.
        partner = self.env["res.partner"].create(
            {"name": "Bad number", "phone": "not-a-number"}
        )
        sub = self._new_subscription(partner=partner)
        self.assertFalse(sub.can_send_sms)
        with self.assertRaises(UserError):
            sub.action_send_sms_payment_reminder()

    def test_can_send_sms_true_with_valid_phone(self):
        sub = self._new_subscription()
        self.assertTrue(sub.can_send_sms)

    # --- behaviour: who/what gets sent --------------------------------

    def test_reminder_uses_correct_template_and_record(self):
        # Mock only the external gateway call, but capture the composer it
        # was called on, so we verify the *real* logic (which template, which
        # record) instead of just the chatter note.
        sub = self._new_subscription()
        captured = {}

        def capture(composer):
            captured["template_id"] = composer.template_id
            captured["res_id"] = composer.res_id
            captured["res_model"] = composer.res_model
            return True

        with patch(SEND_SMS, autospec=True, side_effect=capture):
            sub.action_send_sms_payment_reminder()
        self.assertEqual(captured["res_model"], "sale.subscription")
        self.assertEqual(captured["res_id"], sub.id)
        self.assertEqual(
            captured["template_id"],
            self.env.ref("subscription_oca_sms.sms_template_payment_reminder"),
        )

    def test_failure_uses_correct_template_and_record(self):
        sub = self._new_subscription()
        captured = {}

        def capture(composer):
            captured["template_id"] = composer.template_id
            captured["res_id"] = composer.res_id
            return True

        with patch(SEND_SMS, autospec=True, side_effect=capture):
            sub.action_send_sms_payment_failure()
        self.assertEqual(captured["res_id"], sub.id)
        self.assertEqual(
            captured["template_id"],
            self.env.ref("subscription_oca_sms.sms_template_payment_failure"),
        )

    def test_reminder_body_renders_subscription_data(self):
        # Guards against a silent break if partner_id/name placeholders drift.
        sub = self._new_subscription()
        template = self.env.ref("subscription_oca_sms.sms_template_payment_reminder")
        body = template._render_field("body", sub.ids)[sub.id]
        self.assertIn(sub.partner_id.name, body)
        self.assertIn(sub.name, body)

    def test_send_payment_reminder_logs_chatter(self):
        sub = self._new_subscription()
        with patch(SEND_SMS, return_value=True):
            sub.action_send_sms_payment_reminder()
        self.assertTrue(
            any("Payment reminder SMS sent" in (m.body or "") for m in sub.message_ids)
        )
