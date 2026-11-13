# Copyright 2026 Domatix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalSubscription(CustomerPortal):
    @http.route(
        ["/my/subscriptions/<int:subscription_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_subscription_detail(
        self, subscription_id, access_token=None, report_type=None, download=False, **kw
    ):
        try:
            subscription_sudo = self._document_check_access(
                "sale.subscription", subscription_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        if report_type in ("html", "pdf", "text"):
            return self._show_report(
                model=subscription_sudo,
                report_type=report_type,
                report_ref="subscription_oca.action_report_sale_subscription",
                download=download,
            )
        values = {
            "page_name": "Subscriptions",
            "subscription": subscription_sudo,
            "report_type": "html",
        }
        values = self._get_page_view_values(
            subscription_sudo,
            access_token,
            values,
            "my_subscriptions_history",
            False,
            **kw,
        )
        return request.render(
            "subscription_oca_portal.portal_subscription_page", values
        )
