# Copyright 2026 Domatix - Alvaro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    can_send_sms = fields.Boolean(
        string="Can send SMS",
        compute="_compute_can_send_sms",
        help="Technical field: true when the customer has a valid phone number.",
    )

    @api.depends("partner_id.phone")
    def _compute_can_send_sms(self):
        for subscription in self:
            partner = subscription.partner_id
            subscription.can_send_sms = bool(
                partner and partner._phone_format(fname="phone")
            )

    def _send_sms_template(self, template_xmlid):
        self.ensure_one()
        template = self.env.ref(template_xmlid, raise_if_not_found=False)
        if not template:
            raise UserError(
                self.env._(
                    "SMS template %(xmlid)s is not available.",
                    xmlid=template_xmlid,
                )
            )
        # Validate against the *sanitized* number, mirroring what the SMS
        # composer does internally (it resolves and formats partner_id.phone).
        # A non-empty but invalid number would otherwise pass a naive check
        # and fail later inside the composer with a less helpful message.
        if not self.partner_id._phone_format(fname="phone"):
            raise UserError(
                self.env._(
                    "Cannot send SMS: %(partner)s has no valid phone number.",
                    partner=self.partner_id.display_name,
                )
            )
        composer = (
            self.env["sms.composer"]
            .with_context(active_id=self.id, active_model="sale.subscription")
            .create(
                {
                    "composition_mode": "comment",
                    "res_model": "sale.subscription",
                    "template_id": template.id,
                }
            )
        )
        composer.action_send_sms()

    def action_send_sms_payment_reminder(self):
        self.ensure_one()
        self._send_sms_template("subscription_oca_sms.sms_template_payment_reminder")
        self.message_post(body=self.env._("Payment reminder SMS sent."))

    def action_send_sms_payment_failure(self):
        self.ensure_one()
        self._send_sms_template("subscription_oca_sms.sms_template_payment_failure")
        self.message_post(body=self.env._("Payment failure SMS sent."))
