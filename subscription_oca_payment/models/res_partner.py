# Copyright 2026 Open User Systems - Chris Mann
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    subscription_payment_token_id = fields.Many2one(
        comodel_name="payment.token",
        string="Subscription Payment Token",
        domain="[('partner_id', 'child_of', commercial_partner_id)]",
        help="Charged for subscriptions with automatic payment that have no "
        "payment token of their own.",
    )

    @api.constrains("subscription_payment_token_id")
    def _check_subscription_payment_token_partner(self):
        for partner in self.filtered("subscription_payment_token_id"):
            token = partner.subscription_payment_token_id
            if token.partner_id.commercial_partner_id != partner.commercial_partner_id:
                raise ValidationError(
                    self.env._(
                        "Payment token '%s' belongs to a different partner.",
                        token.display_name,
                    )
                )
