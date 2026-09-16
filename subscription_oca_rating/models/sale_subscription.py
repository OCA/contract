# Copyright 2026 Domatix - Alvaro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import models

logger = logging.getLogger(__name__)

RATING_TEMPLATE = "subscription_oca_rating.mail_template_subscription_rating_request"


class SaleSubscription(models.Model):
    _name = "sale.subscription"
    _inherit = ["rating.mixin", "sale.subscription"]

    def _get_rating_request_template(self):
        return self.env.ref(RATING_TEMPLATE, raise_if_not_found=False)

    def action_send_rating_request(self):
        """Send the rating request email. ``rating_send_request`` creates the
        pending ``rating.rating`` (and its access token) and posts the template
        on the chatter, so the customer receives a working ``/rate`` link."""
        self.ensure_one()
        template = self._get_rating_request_template()
        if not template:
            return False
        self.rating_send_request(template)
        return True

    def close_subscription(self, close_reason_id=False):
        result = super().close_subscription(close_reason_id=close_reason_id)
        self._send_closing_rating_request()
        return result

    def _send_closing_rating_request(self):
        """Automatically ask the customer for a rating when the subscription is
        closed (both the manual close wizard and the cron go through
        ``close_subscription``). Failures here must not roll back the close."""
        self.ensure_one()
        if not self._rating_get_partner().email:
            return
        template = self._get_rating_request_template()
        if not template:
            return
        try:
            self.rating_send_request(template)
        except Exception:
            logger.exception(
                "Could not send the closing rating request for subscription %s",
                self.display_name,
            )
