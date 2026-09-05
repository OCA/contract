# Copyright 2026 Domatix - Alvaro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError, UserError
from odoo.tests import new_test_user

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.product.tests.common import ProductCommon


class TestSubscriptionChangePartner(ProductCommon, BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.pricelist_a = cls.env["product.pricelist"].create({"name": "PL A"})
        cls.pricelist_b = cls.env["product.pricelist"].create({"name": "PL B"})
        cls.partner_a = cls.env["res.partner"].create({"name": "Partner A"})
        cls.partner_b = cls.env["res.partner"].create({"name": "Partner B"})
        cls.product = cls._create_product(
            name="CC product",
            lst_price=10.0,
            subscribable=True,
            uom_id=cls.uom_unit.id,
            taxes_id=[(6, 0, [])],
        )
        cls.template = cls.env["sale.subscription.template"].create(
            {
                "name": "CC template",
                "code": "CC",
                "recurring_rule_type": "months",
                "recurring_interval": 1,
            }
        )
        cls.stage = cls.env["sale.subscription.stage"].search(
            [("type", "=", "in_progress")], limit=1
        )

    def _new_subscription(self, partner=None, pricelist=None):
        partner = partner or self.partner_a
        pricelist = pricelist or self.pricelist_a
        sub = self.env["sale.subscription"].create(
            {
                "partner_id": partner.id,
                "template_id": self.template.id,
                "pricelist_id": pricelist.id,
                "stage_id": self.stage.id,
            }
        )
        self.env["sale.subscription.line"].create(
            {
                "sale_subscription_id": sub.id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "price_unit": 10.0,
                "tax_ids": [(6, 0, [])],
            }
        )
        return sub

    def _make_wizard(self, subscriptions, **values):
        return (
            self.env["sale.subscription.change.partner.wizard"]
            .with_context(active_ids=subscriptions.ids)
            .create({"partner_id": self.partner_b.id, **values})
        )

    def test_change_partner_writes_partner(self):
        sub = self._new_subscription()
        wizard = self._make_wizard(sub)
        wizard.action_apply()
        self.assertEqual(sub.partner_id, self.partner_b)

    def test_change_partner_updates_pricelist_when_flagged(self):
        self.partner_b.property_product_pricelist = self.pricelist_b
        sub = self._new_subscription(pricelist=self.pricelist_a)
        wizard = self._make_wizard(sub, update_pricelist=True)
        wizard.action_apply()
        self.assertEqual(sub.pricelist_id, self.pricelist_b)

    def test_change_partner_keeps_pricelist_when_new_partner_has_none(self):
        # When the new customer has no sale pricelist, the current one is kept
        # even with the flag on (the "honest minimal" path).
        self.partner_b.property_product_pricelist = False
        sub = self._new_subscription(pricelist=self.pricelist_a)
        wizard = self._make_wizard(sub, update_pricelist=True)
        wizard.action_apply()
        self.assertEqual(sub.pricelist_id, self.pricelist_a)

    def test_change_partner_keeps_pricelist_when_unflagged(self):
        self.partner_b.property_product_pricelist = self.pricelist_b
        sub = self._new_subscription(pricelist=self.pricelist_a)
        wizard = self._make_wizard(sub, update_pricelist=False)
        wizard.action_apply()
        self.assertEqual(sub.pricelist_id, self.pricelist_a)

    def test_change_partner_recomputes_fiscal_position_when_flagged(self):
        fpos = self.env["account.fiscal.position"].create(
            {"name": "FP B", "company_id": self.env.company.id}
        )
        self.partner_b.with_company(
            self.env.company
        ).property_account_position_id = fpos
        sub = self._new_subscription()
        self.assertFalse(sub.fiscal_position_id)
        self._make_wizard(sub, update_fiscal_position=True).action_apply()
        self.assertEqual(sub.fiscal_position_id, fpos)

    def test_change_partner_keeps_fiscal_position_when_unflagged(self):
        fpos = self.env["account.fiscal.position"].create(
            {"name": "FP B", "company_id": self.env.company.id}
        )
        self.partner_b.with_company(
            self.env.company
        ).property_account_position_id = fpos
        sub = self._new_subscription()
        self._make_wizard(sub, update_fiscal_position=False).action_apply()
        self.assertFalse(sub.fiscal_position_id)

    def test_change_partner_logs_chatter_message(self):
        sub = self._new_subscription()
        self._make_wizard(sub).action_apply()
        self.assertIn("Customer changed", sub.message_ids[0].body)

    def test_change_partner_same_partner_is_noop(self):
        sub = self._new_subscription(partner=self.partner_b)
        before = len(sub.message_ids)
        self._make_wizard(sub).action_apply()
        self.assertEqual(sub.partner_id, self.partner_b)
        # No change posted: same partner must not produce chatter noise.
        self.assertEqual(len(sub.message_ids), before)

    def test_change_partner_on_closed_raises(self):
        sub = self._new_subscription()
        sub.close_subscription()
        wizard = self._make_wizard(sub)
        with self.assertRaises(UserError):
            wizard.action_apply()

    def test_change_partner_bulk(self):
        subs = (
            self._new_subscription()
            | self._new_subscription()
            | self._new_subscription()
        )
        wizard = self._make_wizard(subs)
        wizard.action_apply()
        for sub in subs:
            self.assertEqual(sub.partner_id, self.partner_b)

    def test_change_partner_requires_manager_group(self):
        sub = self._new_subscription()
        salesman = new_test_user(
            self.env,
            login="cc_salesman",
            groups="sales_team.group_sale_salesman",
        )
        with self.assertRaises(AccessError):
            (
                self.env["sale.subscription.change.partner.wizard"]
                .with_user(salesman)
                .with_context(active_ids=sub.ids)
                .create({"partner_id": self.partner_b.id})
            )


class TestSubscriptionChangePartnerInvoicing(AccountTestInvoicingCommon):
    """Covers the business value of the wizard: future invoices use the new
    customer while already issued invoices keep their original one."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env.user.group_ids += cls.env.ref("sales_team.group_sale_manager")
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "CC invoicing PL", "currency_id": cls.company.currency_id.id}
        )
        cls.template = cls.env["sale.subscription.template"].create(
            {
                "name": "CC invoicing template",
                "code": "CCI",
                "recurring_rule_type": "months",
                "recurring_interval": 1,
                "invoicing_mode": "draft",
            }
        )
        cls.stage = cls.env["sale.subscription.stage"].search(
            [("type", "=", "in_progress")], limit=1
        )

    def _new_subscription(self, partner):
        sub = self.env["sale.subscription"].create(
            {
                "partner_id": partner.id,
                "template_id": self.template.id,
                "pricelist_id": self.pricelist.id,
                "stage_id": self.stage.id,
            }
        )
        self.env["sale.subscription.line"].create(
            {
                "sale_subscription_id": sub.id,
                "product_id": self.product_a.id,
                "product_uom_qty": 1.0,
                "price_unit": 100.0,
                "tax_ids": [(6, 0, [])],
            }
        )
        return sub

    def _change_to(self, sub, partner):
        self.env["sale.subscription.change.partner.wizard"].with_context(
            active_ids=sub.ids
        ).create({"partner_id": partner.id, "update_pricelist": False}).action_apply()

    def test_future_invoice_uses_new_partner(self):
        sub = self._new_subscription(self.partner_a)
        self._change_to(sub, self.partner_b)
        invoice = sub.create_invoice()
        self.assertEqual(invoice.partner_id, self.partner_b)

    def test_issued_invoice_is_not_reassigned(self):
        sub = self._new_subscription(self.partner_a)
        invoice = sub.create_invoice()
        invoice.action_post()
        self._change_to(sub, self.partner_b)
        self.assertEqual(sub.partner_id, self.partner_b)
        self.assertEqual(invoice.partner_id, self.partner_a)
