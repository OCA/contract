# Copyright 2023 ooops404
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import TransactionCase


class TestSubscriptionOCA(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "pricelist for contract test"}
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "partner test subscription_oca",
                "property_product_pricelist": cls.pricelist.id,
                "email": "demo1@demo.com",
            }
        )
        cls.partner_2 = cls.env["res.partner"].create(
            {
                "name": "partner test subscription_oca 2",
                "property_product_pricelist": cls.pricelist.id,
                "email": "demo2@demo.com",
            }
        )
        cls.tax_10pc_incl = cls.env["account.tax"].create(
            {
                "name": "10% Tax incl",
                "amount_type": "percent",
                "amount": 10,
                "price_include": True,
            }
        )
        cls.product_1 = cls.env.ref("product.product_product_1")
        cls.product_1.taxes_id = [(6, 0, cls.tax_10pc_incl.ids)]
        cls.product_2 = cls.env.ref("product.product_product_2")
        cls.country = cls.env["res.country"].search([], limit=1)
        cls.fiscal = cls.env["account.fiscal.position"].create(
            {
                "name": "Regime National",
                "auto_apply": True,
                "country_id": cls.country.id,
                "vat_required": True,
                "sequence": 10,
            }
        )
        cls.tmpl = cls.env["sale.subscription.template"].create(
            {
                "name": "Test Template",
                "code": "OMG",
                "description": "Some sort of subscription terms",
                "product_ids": [(6, 0, [cls.product_1.id, cls.product_2.id])],
            }
        )
        cls.stage = cls.env["sale.subscription.stage"].create(
            {
                "name": "Test Sub Stage",
            }
        )
        cls.tag = cls.env["sale.subscription.tag"].create(
            {
                "name": "Test Tag",
            }
        )
        cls.sub = cls.env["sale.subscription"].create(
            {
                "company_id": 1,
                "partner_id": cls.partner.id,
                "template_id": cls.tmpl.id,
                "tag_ids": [(6, 0, [cls.tag.id])],
                "stage_id": cls.stage.id,
                "pricelist_id": cls.pricelist.id,
                "fiscal_position_id": cls.fiscal.id,
            }
        )
        cls.sub_line = cls.env["sale.subscription.line"].create(
            {
                "company_id": 1,
                "sale_subscription_id": cls.sub.id,
                "product_id": cls.product_1.id,
            }
        )
        cls.close_reason = cls.env["sale.subscription.close.reason"].create(
            {
                "name": "Test Close Reason",
            }
        )

    def test_subscription_oca_sale_order(self):
        # SO standard flow
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_1.name,
                            "product_id": self.product_1.id,
                            "product_uom_qty": 2,
                            "product_uom": self.product_1.uom_id.id,
                            "price_unit": self.product_1.list_price,
                        },
                    )
                ],
            }
        )
        so._compute_subscriptions_count()
        self.assertEqual(so.subscriptions_count, 0)
        action = so.action_view_subscriptions()
        self.assertIsInstance(action, dict)
        so.action_confirm()  # without subs.

    def test_subscription_oca_sub_line(self):
        # sale.subscription.line
        self.assertEqual(self.sub_line.name, self.sub_line.product_id.name)
        self.assertIsNotNone(self.sub_line.tax_ids)
        self.assertEqual(self.sub_line.price_unit, 30.75)
        self.assertEqual(self.sub_line.discount, 0)
        res = self.sub_line._get_display_price(self.product_2)
        self.assertEqual(res, 38.25)
        sol_res = self.sub_line._prepare_sale_order_line()
        self.assertIsInstance(sol_res, dict)
        move_res = self.sub_line._prepare_account_move_line()
        self.assertIsInstance(move_res, dict)

    def test_subscription_oca_sub_cron(self):
        # sale.subscription
        self.sub.cron_subscription_management()
        # invoice should be created by cron
        inv_id = self.env["account.move"].search(
            [("subscription_id", "=", self.sub.id)]
        )
        self.assertEqual(len(inv_id), 1)
        self.assertEqual(self.sub.recurring_total, 27.95)
        self.assertEqual(self.sub.amount_total, 30.75)

    def test_subscription_oca_sub_workflow(self):
        sale_order = self.sub.create_sale_order()
        self.assertTrue(sale_order)
        move_id = self.sub.create_invoice()
        self.assertTrue(move_id)
        res = self.sub.manual_invoice()
        self.assertEqual(res["type"], "ir.actions.act_window")
        inv_ids = self.env["account.move"].search(
            [("subscription_id", "=", self.sub.id)]
        )
        self.assertEqual(len(inv_ids), 2)
        self.assertEqual(sum(inv_ids.mapped("amount_total")), 2 * 30.75)
        self.assertEqual(self.sub.account_invoice_ids_count, 2)
        res = self.sub.action_view_account_invoice_ids()
        self.assertEqual(res["type"], "ir.actions.act_window")
        self.assertEqual(self.sub.sale_order_ids_count, 1)
        res = self.sub.action_view_sale_order_ids()
        self.assertIn(str(self.sub.sale_order_ids.id), str(res["domain"]))
        self.sub.calculate_recurring_next_date(fields.Datetime.now())
        self.assertEqual(
            self.sub.recurring_next_date,
            fields.Date.today() + relativedelta(months=1),
        )
        self.sub.partner_id = self.partner_2
        self.sub.onchange_partner_id()
        self.assertEqual(
            self.sub.pricelist_id.id, self.partner_2.property_product_pricelist.id
        )
        self.sub.onchange_partner_id_fpos()
        self.assertFalse(self.sub.fiscal_position_id)
        res = self.sub.action_close_subscription()
        self.assertEqual(res["type"], "ir.actions.act_window")

    def test_subscription_oca_sub_stage(self):
        # sale.subscription.stage
        self.stage._check_lot_product()  # should not raise
