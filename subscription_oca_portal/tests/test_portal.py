# Copyright 2026 Domatix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import HttpCase, TransactionCase, tagged


class SubscriptionPortalCommon:
    @classmethod
    def _create_subscription(cls):
        partner = cls.env["res.partner"].create({"name": "Portal customer"})
        pricelist = cls.env["product.pricelist"].create({"name": "Portal pricelist"})
        template = cls.env["sale.subscription.template"].create(
            {"name": "Portal template"}
        )
        return cls.env["sale.subscription"].create(
            {
                "partner_id": partner.id,
                "pricelist_id": pricelist.id,
                "template_id": template.id,
            }
        )


@tagged("post_install", "-at_install")
class TestSubscriptionPortal(SubscriptionPortalCommon, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.subscription = cls._create_subscription()

    def test_action_preview(self):
        action = self.subscription.action_preview()
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertIn(f"/my/subscriptions/{self.subscription.id}", action["url"])
        self.assertIn("access_token=", action["url"])


@tagged("post_install", "-at_install")
class TestSubscriptionPortalHttp(SubscriptionPortalCommon, HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.subscription = cls._create_subscription()

    def test_portal_page(self):
        url = (
            f"/my/subscriptions/{self.subscription.id}"
            f"?access_token={self.subscription._portal_ensure_token()}"
        )
        self.assertEqual(self.url_open(url).status_code, 200)

    def test_portal_page_requires_token(self):
        url = f"/my/subscriptions/{self.subscription.id}"
        response = self.url_open(url, allow_redirects=False)
        self.assertIn(response.status_code, (302, 303))

    def test_report_html(self):
        url = (
            f"/my/subscriptions/{self.subscription.id}"
            f"?access_token={self.subscription._portal_ensure_token()}"
            "&report_type=html"
        )
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.subscription.name.encode(), response.content)

    def test_report_base_filename(self):
        self.assertEqual(
            self.subscription._get_report_base_filename(),
            f"Subscription - {self.subscription.name}",
        )
