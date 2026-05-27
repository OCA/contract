# Copyright 2026 Domatix - Alvaro Domatix
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError
from odoo.tests.common import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestSubscriptionSecurity(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.company_a = cls.env["res.company"].create({"name": "Company A"})
        cls.company_b = cls.env["res.company"].create({"name": "Company B"})

        cls.user_company_a = new_test_user(
            cls.env,
            login="subscription_oca_user_company_a",
            groups="sales_team.group_sale_salesman",
            company_id=cls.company_a.id,
            company_ids=[(6, 0, [cls.company_a.id])],
        )
        cls.user_company_b = new_test_user(
            cls.env,
            login="subscription_oca_user_company_b",
            groups="sales_team.group_sale_salesman",
            company_id=cls.company_b.id,
            company_ids=[(6, 0, [cls.company_b.id])],
        )

        cls.pricelist_a = cls.env["product.pricelist"].create(
            {"name": "Pricelist A", "company_id": cls.company_a.id}
        )
        cls.pricelist_b = cls.env["product.pricelist"].create(
            {"name": "Pricelist B", "company_id": cls.company_b.id}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Multi-company partner"})
        cls.template = cls.env["sale.subscription.template"].create(
            {
                "name": "Multi-company template",
                "code": "MC-TMPL",
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Multi-company product", "subscribable": True}
        )

        cls.subscription_a = cls.env["sale.subscription"].create(
            {
                "company_id": cls.company_a.id,
                "partner_id": cls.partner.id,
                "template_id": cls.template.id,
                "pricelist_id": cls.pricelist_a.id,
            }
        )
        cls.subscription_b = cls.env["sale.subscription"].create(
            {
                "company_id": cls.company_b.id,
                "partner_id": cls.partner.id,
                "template_id": cls.template.id,
                "pricelist_id": cls.pricelist_b.id,
            }
        )
        cls.line_a = cls.env["sale.subscription.line"].create(
            {
                "sale_subscription_id": cls.subscription_a.id,
                "product_id": cls.product.id,
            }
        )
        cls.line_b = cls.env["sale.subscription.line"].create(
            {
                "sale_subscription_id": cls.subscription_b.id,
                "product_id": cls.product.id,
            }
        )

    def test_user_can_read_own_company_subscription(self):
        subscription = self.subscription_a.with_user(self.user_company_a)
        subscription.read(["name"])

    def test_user_cannot_read_other_company_subscription(self):
        subscription = self.subscription_b.with_user(self.user_company_a)
        with self.assertRaises(AccessError):
            subscription.read(["name"])

    def test_user_cannot_search_other_company_subscription(self):
        found = (
            self.env["sale.subscription"]
            .with_user(self.user_company_a)
            .search([("id", "=", self.subscription_b.id)])
        )
        self.assertFalse(found)

    def test_user_cannot_read_other_company_subscription_line(self):
        line = self.line_b.with_user(self.user_company_a)
        with self.assertRaises(AccessError):
            line.read(["name"])

    def test_user_can_read_own_company_subscription_line(self):
        line = self.line_a.with_user(self.user_company_a)
        line.read(["name"])

    def test_user_cannot_write_other_company_subscription(self):
        # The rule applies to write too, not only read/search.
        subscription = self.subscription_b.with_user(self.user_company_a)
        with self.assertRaises(AccessError):
            subscription.write({"description": "hack"})

    def test_company_b_user_cannot_read_company_a_subscription(self):
        # Symmetry: isolation works both ways.
        subscription = self.subscription_a.with_user(self.user_company_b)
        with self.assertRaises(AccessError):
            subscription.read(["name"])
