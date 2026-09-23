# Copyright 2023 ooops404
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import uuid
from unittest.mock import patch

from dateutil.relativedelta import relativedelta

from odoo import Command, exceptions, fields
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


class TestSubscriptionOCA(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.portal_user = cls.env.ref("base.demo_user0")
        cls.cash_journal = cls.env["account.journal"].search(
            [
                ("type", "=", "cash"),
                ("company_id", "=", cls.env.ref("base.main_company").id),
            ],
            limit=1,
        )
        cls.sale_journal = cls.env["account.journal"].search(
            [
                ("type", "=", "sale"),
                ("company_id", "=", cls.env.ref("base.main_company").id),
            ],
            limit=1,
        )
        cls.pricelist1 = cls.env["product.pricelist"].create(
            {
                "name": "pricelist for contract test",
            }
        )
        cls.pricelist2 = cls.env["product.pricelist"].create(
            {
                "name": "pricelist for contract test 2",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "partner test subscription_oca",
                "property_product_pricelist": cls.pricelist1.id,
                "email": "demo1@demo.com",
            }
        )
        cls.partner_2 = cls.env["res.partner"].create(
            {
                "name": "partner test subscription_oca 2",
                "property_product_pricelist": cls.pricelist1.id,
                "email": "demo2@demo.com",
            }
        )
        cls.tax_10pc_incl = cls.env["account.tax"].create(
            {
                "name": "10% Tax incl",
                "amount_type": "percent",
                "amount": 10,
                "price_include_override": "tax_included",
            }
        )
        cls.tax_0pc = cls.env["account.tax"].create(
            {
                "name": "0% Tax",
                "amount_type": "percent",
                "amount": 0,
            }
        )
        cls.product_1 = cls.env.ref("product.product_product_5")
        cls.product_1.list_price = 30.75
        cls.product_1.subscribable = True
        cls.product_1.taxes_id = [Command.set(cls.tax_10pc_incl.ids)]
        cls.product_2 = cls.env.ref("product.product_product_6")
        cls.product_2.list_price = 38.25
        cls.product_2.taxes_id = [Command.set(cls.tax_0pc.ids)]
        cls.product_2.subscribable = True

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

        cls.tmpl1 = cls.create_sub_template({})
        cls.tmpl2 = cls.create_sub_template(
            {
                "recurring_rule_boundary": "limited",
                "recurring_rule_type": "days",
            }
        )
        cls.tmpl3 = cls.create_sub_template(
            {
                "recurring_rule_boundary": "unlimited",
                "recurring_rule_type": "weeks",
            }
        )
        cls.tmpl4 = cls.create_sub_template(
            {
                "recurring_rule_boundary": "limited",
                "invoicing_mode": "invoice",
                "recurring_rule_type": "years",
            }
        )
        cls.tmpl5 = cls.create_sub_template(
            {
                "recurring_rule_boundary": "unlimited",
                "invoicing_mode": "invoice",
                "recurring_rule_type": "days",
            }
        )

        cls.stage = cls.env["sale.subscription.stage"].create(
            {
                "name": "Test Sub Stage",
            }
        )
        cls.stage_2 = cls.env["sale.subscription.stage"].create(
            {
                "name": "Test Sub Stage 2",
                "type": "pre",
            }
        )
        cls.tag = cls.env["sale.subscription.tag"].create(
            {
                "name": "Test Tag",
            }
        )

        cls.sub1 = cls.create_sub({})
        cls.sub2 = cls.create_sub(
            {
                "template_id": cls.tmpl3.id,
            }
        )
        cls.sub3 = cls.create_sub(
            {
                "template_id": cls.tmpl2.id,
                "pricelist_id": cls.pricelist2.id,
            }
        )
        cls.sub4 = cls.create_sub(
            {
                "template_id": cls.tmpl3.id,
                "recurring_rule_boundary": False,
                "date_start": fields.Date.today(),
            }
        )
        cls.sub5 = cls.create_sub(
            {
                "template_id": cls.tmpl4.id,
                "pricelist_id": cls.pricelist2.id,
                "date_start": fields.Date.today(),
                "recurring_next_date": fields.Date.today() - relativedelta(days=1),
            }
        )
        cls.sub6 = cls.create_sub(
            {
                "template_id": cls.tmpl5.id,
                "recurring_rule_boundary": False,
                "date_start": "2099-01-01",
            }
        )
        cls.sub7 = cls.create_sub(
            {
                "template_id": cls.tmpl2.id,
                "pricelist_id": cls.pricelist2.id,
                "date_start": fields.Date.today() - relativedelta(days=100),
                "in_progress": True,
            }
        )
        cls.sub8 = cls.create_sub(
            {
                "template_id": cls.tmpl2.id,
                "pricelist_id": cls.pricelist2.id,
                "date_start": fields.Date.today() - relativedelta(days=100),
                "in_progress": True,
                "journal_id": cls.cash_journal.id,
            }
        )
        cls.sub9 = cls.create_sub(
            {
                "template_id": cls.tmpl3.id,
                "date_start": fields.Date.today() - relativedelta(days=100),
                "in_progress": True,
                "recurring_rule_boundary": True,
            }
        )

        cls.sub_line = cls.create_sub_line(cls.sub1)
        cls.sub_line2 = cls.env["sale.subscription.line"].create(
            {
                "company_id": 1,
                "sale_subscription_id": cls.sub1.id,
            }
        )
        cls.sub_line21 = cls.create_sub_line(cls.sub2)
        cls.sub_line22 = cls.create_sub_line(cls.sub2, cls.product_2.id)
        cls.sub_line31 = cls.create_sub_line(cls.sub3)
        cls.sub_line32 = cls.create_sub_line(cls.sub3, cls.product_2.id)
        cls.sub_line41 = cls.create_sub_line(cls.sub4)
        cls.sub_line42 = cls.create_sub_line(cls.sub4, cls.product_2.id)
        cls.sub_line51 = cls.create_sub_line(cls.sub5)
        cls.sub_line52 = cls.create_sub_line(cls.sub5, cls.product_2.id)
        cls.sub_line71 = cls.create_sub_line(cls.sub7)
        cls.sub_line72 = cls.create_sub_line(cls.sub7, cls.product_2.id)

        cls.close_reason = cls.env["sale.subscription.close.reason"].create(
            {
                "name": "Test Close Reason",
            }
        )
        cls.sub_line2.read(["name", "price_unit"])
        cls.sub_line2.unlink()

        # Pricelists.
        cls.pricelist_l1 = cls._create_price_list("Level 1")
        cls.pricelist_l2 = cls._create_price_list("Level 2")
        cls.pricelist_l3 = cls._create_price_list("Level 3")
        cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist_l3.id,
                "applied_on": "0_product_variant",
                "compute_price": "formula",
                "base": "pricelist",
                "base_pricelist_id": cls.pricelist_l1.id,
                "product_id": cls.product_1.id,
            }
        )
        cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist_l2.id,
                "applied_on": "3_global",
                "compute_price": "formula",
                "base": "pricelist",
                "base_pricelist_id": cls.pricelist_l1.id,
            }
        )
        cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist_l1.id,
                "applied_on": "3_global",
                "compute_price": "formula",
                "base": "standard_price",
                "fixed_price": 1000,
            }
        )

    @classmethod
    def create_sub_template(cls, vals):
        code = str(uuid.uuid4().hex)
        default_vals = {
            "name": "Test Template " + code,
            "code": code,
            "description": "Some sort of subscription terms",
            "product_ids": [Command.set([cls.product_1.id, cls.product_2.id])],
        }
        default_vals.update(vals)
        rec = cls.env["sale.subscription.template"].create(default_vals)
        return rec

    @classmethod
    def create_sub(cls, vals):
        default_vals = {
            "company_id": 1,
            "partner_id": cls.partner.id,
            "template_id": cls.tmpl1.id,
            "tag_ids": [Command.set([cls.tag.id])],
            "stage_id": cls.stage.id,
            "pricelist_id": cls.pricelist1.id,
            "fiscal_position_id": cls.fiscal.id,
        }
        default_vals.update(vals)
        rec = cls.env["sale.subscription"].create(default_vals)
        return rec

    @classmethod
    def create_sub_line(cls, sub, prod=None):
        ssl = cls.env["sale.subscription.line"].create(
            {
                "company_id": 1,
                "sale_subscription_id": sub.id,
                "product_id": prod or cls.product_1.id,
            }
        )
        return ssl

    @classmethod
    def _create_price_list(cls, name):
        return cls.env["product.pricelist"].create(
            {
                "name": name,
                "active": True,
                "currency_id": cls.env.ref("base.USD").id,
                "company_id": cls.env.user.company_id.id,
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
                    Command.create(
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
        so.with_context(uid=1).action_confirm()  # without subs.

    def test_subscription_oca_sub_lines(self):
        # sale.subscription.line
        self.assertEqual(self.sub_line.name, self.sub_line.product_id.display_name)
        self.assertIsNotNone(self.sub_line.tax_ids)
        self.assertAlmostEqual(self.sub_line.price_unit, 30.75, 2)
        self.assertEqual(self.sub_line.discount, 0)
        res = self.sub_line._get_display_price(self.product_2)
        self.assertAlmostEqual(res, 38.25, 2)
        sol_res = self.sub_line._prepare_sale_order_line()
        self.assertIsInstance(sol_res, dict)
        move_res = self.sub_line._prepare_account_move_line()
        self.assertIsInstance(move_res, dict)

    def test_subscription_oca_sub_cron_error(self):
        # The cron wraps each subscription in a savepoint and logs errors rather
        # than re-raising, so one failure never aborts the rest of the batch.
        sub = self.create_sub(
            {
                "date_start": fields.Date.today() - relativedelta(days=10),
                "in_progress": True,
            }
        )
        self.create_sub_line(sub)
        sub.recurring_next_date = fields.Date.today() - relativedelta(days=1)
        SaleSubscription = type(self.env["sale.subscription"])
        # Limit the cron to only our test subscription so the mock's side-effect
        # doesn't fire on other in-progress subscriptions that call
        # generate_invoice() outside the savepoint path.
        with patch.object(
            SaleSubscription,
            "search",
            return_value=sub,
        ):
            with patch.object(
                SaleSubscription,
                "generate_invoice",
                side_effect=exceptions.UserError("Error"),
            ):
                with mute_logger(
                    "odoo.addons.subscription_oca.models.sale_subscription"
                ):
                    sub.cron_subscription_management()
        # No invoice should have been created (the savepoint rolled it back).
        self.assertEqual(
            self.env["account.move"].search_count([("subscription_id", "=", sub.id)]),
            0,
        )

    def test_subscription_oca_sub_cron(self):
        # sale.subscription
        self.sub1.cron_subscription_management()
        # invoice should be created by cron
        inv_id = self.env["account.move"].search(
            [("subscription_id", "=", self.sub1.id)]
        )
        self.assertEqual(len(inv_id), 1)
        self.assertAlmostEqual(self.sub1.recurring_total, 27.95, 2)
        self.assertAlmostEqual(self.sub1.amount_total, 30.75, 2)
        self.assertAlmostEqual(self.sub2.recurring_total, 66.2, 2)
        self.assertEqual(self.sub2.amount_total, 69)

    def test_subscription_oca_sub1_workflow(self):
        res = self._collect_all_sub_test_results(self.sub1)
        self.assertTrue(res[0])
        self.assertTrue(res[1])
        self.assertEqual(res[3], 2)
        self.assertAlmostEqual(res[4], 2 * 30.75, 2)
        self.assertEqual(res[5], 2)
        self.assertEqual(res[7], 1)
        self.assertEqual(
            res[9],
            fields.Date.today() + relativedelta(months=1),
        )
        self.assertEqual(res[10], self.partner_2.property_product_pricelist.id)
        self.assertFalse(res[11])
        self.assertEqual(res[12], "ir.actions.act_window")

    def test_subscription_oca_sub2_workflow(self):
        res = self._collect_all_sub_test_results(self.sub2)
        self.assertTrue(res[0])
        self.assertTrue(res[1])
        self.assertEqual(res[3], 2)
        self.assertEqual(res[4], 138)
        self.assertEqual(res[5], 2)
        self.assertEqual(res[7], 1)
        self.assertEqual(
            res[9],
            fields.Date.today() + relativedelta(weeks=1),
        )
        self.assertEqual(res[10], self.partner_2.property_product_pricelist.id)
        self.assertFalse(res[11])

    def test_subscription_oca_sub3_workflow(self):
        res = self._collect_all_sub_test_results(self.sub3)
        self.assertTrue(res[0])
        self.assertTrue(res[1])
        self.assertEqual(res[3], 2)
        self.assertEqual(res[4], 138)
        self.assertEqual(res[5], 2)
        self.assertEqual(res[6], "ir.actions.act_window")
        self.assertEqual(res[7], 1)
        self.assertEqual(
            res[9],
            fields.Date.today() + relativedelta(days=1),
        )
        self.assertEqual(res[10], self.partner_2.property_product_pricelist.id)
        self.assertFalse(res[11])

    def test_subscription_oca_sub4_workflow(self):
        res = self._collect_all_sub_test_results(self.sub4)
        self.assertTrue(res[0])
        self.assertTrue(res[1])
        self.assertEqual(res[2], "ir.actions.act_window")
        self.assertEqual(res[3], 2)
        self.assertEqual(res[4], 138)
        self.assertEqual(res[5], 2)
        self.assertEqual(res[7], 1)
        self.assertEqual(
            res[9],
            fields.Date.today() + relativedelta(weeks=1),
        )
        self.assertEqual(res[10], self.partner_2.property_product_pricelist.id)
        self.assertFalse(res[11])

    def test_subscription_oca_sub5_workflow(self):
        res = self._collect_all_sub_test_results(self.sub5)
        self.assertTrue(res[0])
        self.assertTrue(res[1])
        self.assertEqual(res[3], 2)
        self.assertEqual(res[4], 138)
        self.assertEqual(res[5], 2)
        self.assertEqual(res[7], 1)
        self.assertEqual(
            res[9],
            fields.Date.today() + relativedelta(years=1),
        )
        self.assertEqual(res[10], self.partner_2.property_product_pricelist.id)
        self.assertFalse(res[11])
        self.sub5.recurring_next_date = fields.Date.today()
        self.sub5.template_id = self.tmpl5
        self.sub5._onchange_template_id()
        self.sub5.invoice_ids.unlink()
        self.sub5._onchange_template_id()

    def test_subscription_oca_sub7_workflow(self):
        res = self._collect_all_sub_test_results(self.sub7.with_context(uom=2))
        self.assertTrue(res[0])
        self.assertTrue(res[1])
        self.assertEqual(res[3], 2)
        self.assertEqual(res[4], 138)
        self.assertEqual(res[5], 2)
        self.assertEqual(res[7], 1)
        self.assertEqual(
            res[9],
            fields.Date.today() + relativedelta(days=1),
        )
        self.assertEqual(res[10], self.partner_2.property_product_pricelist.id)
        self.assertFalse(res[11])

    def test_subscription_oca_sub8_workflow(self):
        subscription = self.sub8
        subscription.create_sale_order()
        with self.assertRaises(exceptions.UserError):
            subscription.create_invoice()
        self.sub8.journal_id = self.sale_journal
        subscription.create_invoice()
        self.sub8.template_id.invoicing_mode = "invoice"
        with self.assertRaises(exceptions.UserError):
            subscription.generate_invoice()
        self.sub8.template_id.invoicing_mode = "invoice_send"
        with self.assertRaises(exceptions.UserError):
            subscription.generate_invoice()
        self.sub8.template_id.invoicing_mode = "sale_and_invoice"
        with self.assertRaises(exceptions.UserError):
            subscription.generate_invoice()
        # add lines and repeat
        self.sub_line81 = self.env["sale.subscription.line"].create(
            {
                "company_id": 1,
                "sale_subscription_id": self.sub8.id,
                "product_id": self.product_1.id,
            }
        )
        self.sub_line82 = self.env["sale.subscription.line"].create(
            {
                "company_id": 1,
                "sale_subscription_id": self.sub8.id,
                "product_id": self.product_2.id,
            }
        )
        subscription.create_sale_order()
        subscription.create_invoice()
        subscription.journal_id = self.sale_journal
        subscription.create_invoice()
        subscription.template_id.invoicing_mode = "invoice"
        subscription.generate_invoice()
        subscription.template_id.invoicing_mode = "invoice_send"
        subscription.generate_invoice()
        subscription.template_id.invoicing_mode = "sale_and_invoice"
        order = subscription.create_sale_order()
        order.with_context(uid=1).action_confirm()
        subscription.sale_subscription_line_ids.mapped("product_id").write(
            {"invoice_policy": "order"}
        )
        subscription.generate_invoice()
        subscription._check_dates("2099-01-01", "2099-01-01")
        subscription._check_dates("2098-01-01", "2099-01-01")
        subscription._check_dates("2098-01-01", "2097-01-01")
        subscription._check_dates(fields.Date.today(), fields.Date.today())
        subscription._check_dates(fields.Datetime.now(), fields.Datetime.now())
        subscription.write({"stage_id": self.stage_2})

    def test_subscription_oca_sub8_workflow_portal(self):
        # portal user
        subscription = self.sub8.with_user(self.portal_user)
        sale_order = subscription.create_sale_order()
        self.assertFalse(sale_order)
        move_id = subscription.with_user(self.portal_user).create_invoice()
        self.assertFalse(move_id)
        with self.assertRaises(exceptions.AccessError):
            subscription.manual_invoice()
        with self.assertRaises(exceptions.AccessError):
            subscription.calculate_recurring_next_date(fields.Datetime.now())
        with self.assertRaises(exceptions.AccessError):
            subscription.partner_id = self.partner_2

    def test_subscription_oca_sub_stage(self):
        # sale.subscription.stage
        self.stage._check_lot_product()  # should not raise

    def test_x_subscription_oca_pricelist_related(self):
        res = self.partner.read(["subscription_count", "subscription_ids"])
        self.assertEqual(res[0]["subscription_count"], 9)
        res = self.partner.action_view_subscription_ids()
        self.assertIsInstance(res, dict)
        sale_order = self.sub1.create_sale_order()
        sale_order.with_context(uid=1).create_subscription(
            sale_order.order_line, self.tmpl1
        )
        sale_order.get_next_interval(
            self.tmpl1.recurring_rule_type, self.tmpl1.recurring_interval
        )
        self.sub_line.product_uom_qty = 100
        self.env.user.groups_id = [
            Command.link(self.env.ref("sale.group_discount_per_so_line").id)
        ]
        disc = self.sub_line.read(["discount"])
        self.assertEqual(disc[0]["discount"], 0)
        wiz = self.env["close.reason.wizard"].create({})
        wiz.with_context(active_id=self.sub1.id).button_confirm()
        self.assertEqual(self.sub1.stage_id.name, "Closed")
        self.assertTrue(self.sub1.active)
        self.tmpl1.action_view_subscription_ids()
        self.tmpl1.action_view_product_ids()
        self.tmpl1.read(["product_ids_count", "subscription_count"])
        with self.assertRaises(exceptions.ValidationError):
            self.env["sale.subscription.stage"].create(
                {
                    "name": "Test Sub Stage",
                    "type": "post",
                }
            )
        pricelist = self.sub_line.sale_subscription_id.pricelist_id.copy(
            {"currency_id": self.env.ref("base.THB").id}
        )
        item1 = self.env["product.pricelist.item"].create(
            {
                "pricelist_id": pricelist.id,
                "product_id": self.product_1.product_variant_id.id,
                "name": "Test special rule 1",
                "applied_on": "0_product_variant",
                "price": 3,
            }
        )
        self.sub_line.sale_subscription_id.pricelist_id = pricelist
        self.sub_line.product_uom_qty = 200
        res = self.sub_line.read(["discount"])
        self.assertEqual(res[0]["discount"], 100)
        item1.unlink()
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": pricelist.id,
                "product_id": self.product_1.product_variant_id.id,
                "name": "Test special rule 2",
                "base": "pricelist",
                "base_pricelist_id": self.pricelist1.id,
                "applied_on": "0_product_variant",
            }
        )
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist1.id,
                "product_id": self.product_1.product_variant_id.id,
                "name": "Test special rule 3",
                "applied_on": "0_product_variant",
                "base": "standard_price",
            }
        )
        self.sub_line.sale_subscription_id.pricelist_id = pricelist
        self.sub_line.product_uom_qty = 300
        res = self.sub_line.read(["discount"])
        self.assertEqual(res[0]["discount"], 100)

    def test_x_subscription_oca_pricelist_related_2(self):
        self.pricelist_l3.currency_id = self.env.ref("base.THB")
        self.sub_line.sale_subscription_id.pricelist_id = self.pricelist_l3
        res = self.sub_line._get_display_price(self.product_1)
        self.assertAlmostEqual(
            int(res),
            round(
                self.product_1.standard_price
                * self.pricelist_l3.currency_id.rate_ids[:1].company_rate
            ),
        )
        self.sub_line.product_uom_qty = 300
        res = self.sub_line.read(["discount"])
        self.assertEqual(res[0]["discount"], 0)

    def test_open_subscription(self):
        invoice = self.sub1.create_invoice()
        action = invoice.action_open_subscription()
        self.assertEqual(action["res_id"], self.sub1.id)

    def _collect_all_sub_test_results(self, subscription):
        """Creates the invoice of a subscription and returns its data
        :param subscription: subscription to invoice
        :returns: Lists with the following data
            returns[0]: Created sale order record
            returns[1]: Created invoice record
            returns[2]: Type of the action to see a manually created invoice
            returns[3]: Number of invoices
            returns[4]: Amount total (wout taxes) of all the invoices
            returns[5]: Invoices count of the subscription
            returns[6]: Type of the action to the subscription invoices
            returns[7]: Sale order count of the subscription
            returns[8]: Id of the sale order
            returns[9]: Recurring next date of the subscription
            returns[10]: Id of the pricelist of the subsciption
            returns[11]: Fiscal position record of the subscription
            returns[12]: Type of the wizard action close a subscription
            returns[13]: Subscription stages
        """
        test_res = []
        sale_order = subscription.create_sale_order()
        test_res.append(sale_order)
        move_id = subscription.create_invoice()
        test_res.append(move_id)
        res = subscription.manual_invoice()
        test_res.append(res["type"])
        inv_ids = self.env["account.move"].search(
            [("subscription_id", "=", subscription.id)]
        )
        test_res.append(len(inv_ids))
        test_res.append(sum(inv_ids.mapped("amount_total")))
        test_res.append(subscription.account_invoice_ids_count)
        res = subscription.action_view_account_invoice_ids()
        test_res.append(res["type"])
        test_res.append(subscription.sale_order_ids_count)
        subscription.action_view_sale_order_ids()
        test_res.append(subscription.sale_order_ids.id)
        subscription.calculate_recurring_next_date(fields.Datetime.now())
        test_res.append(subscription.recurring_next_date)
        subscription.partner_id = self.partner_2
        subscription.onchange_partner_id()
        test_res.append(subscription.pricelist_id.id)
        subscription.onchange_partner_id_fpos()
        test_res.append(subscription.fiscal_position_id)
        res = subscription.action_close_subscription()
        self.assertEqual(res["type"], "ir.actions.act_window")
        test_res.append(res["type"])
        group_stage_ids = subscription._read_group_stage_ids(
            stages=self.env["sale.subscription.stage"].search([]), domain=[]
        )
        test_res.append(group_stage_ids)
        return test_res

    # ------------------------------------------------------------------
    # Automatic payment feature
    # ------------------------------------------------------------------
    def _prepare_provider(self):
        bank_journal = self.env["account.journal"].search(
            [
                ("type", "=", "bank"),
                ("company_id", "=", self.env.ref("base.main_company").id),
            ],
            limit=1,
        )
        if not bank_journal:
            bank_journal = self.env["account.journal"].create(
                {"name": "Test Bank", "type": "bank", "code": "TBNKX"}
            )
        provider = self.env["payment.provider"].create(
            {"name": "Test Provider", "state": "test"}
        )
        provider.journal_id = bank_journal
        # Wire an inbound payment method line so a successful transaction can
        # create and reconcile a payment during post-processing.
        if not provider.journal_id.inbound_payment_method_line_ids.filtered(
            lambda line: line.payment_provider_id == provider
        ):
            self.env["account.payment.method.line"].create(
                {
                    "name": "Test inbound line",
                    "payment_method_id": self.env.ref(
                        "account.account_payment_method_manual_in"
                    ).id,
                    "payment_provider_id": provider.id,
                    "journal_id": provider.journal_id.id,
                }
            )
        return provider

    def _create_payment_token(self, partner, provider):
        method = self.env["payment.method"].create(
            {
                "name": "Test Method",
                "code": "none",
                "provider_ids": [Command.set(provider.ids)],
                "support_tokenization": True,
            }
        )
        return self.env["payment.token"].create(
            {
                "partner_id": partner.id,
                "provider_id": provider.id,
                "provider_ref": f"tok-{partner.id}",
                "payment_method_id": method.id,
            }
        )

    def _post_subscription_invoice(self, subscription):
        invoice = subscription.create_invoice()
        invoice.action_post()
        return invoice

    def test_payment_no_token(self):
        invoice = self._post_subscription_invoice(self.sub1)
        self.assertFalse(self.sub1.create_payment(invoice))
        self.assertTrue(self.sub1.payment_exception)
        msgs = self.sub1.message_ids.filtered(
            lambda m: "No payment token found" in (m.body or "")
        )
        self.assertEqual(len(msgs), 1)

    def test_payment_success(self):
        provider = self._prepare_provider()
        self.sub1.payment_token_id = self._create_payment_token(self.partner, provider)
        invoice = self._post_subscription_invoice(self.sub1)
        tx_model = type(self.env["payment.transaction"])

        def _fake_send(tx):
            tx.state = "done"

        with (
            patch.object(tx_model, "_send_payment_request", _fake_send),
            patch.object(tx_model, "_post_process", lambda tx: None),
        ):
            self.assertTrue(self.sub1.create_payment(invoice))
        self.assertFalse(self.sub1.payment_exception)

    def test_payment_pending_async(self):
        provider = self._prepare_provider()
        self.sub1.payment_token_id = self._create_payment_token(self.partner, provider)
        invoice = self._post_subscription_invoice(self.sub1)
        tx_model = type(self.env["payment.transaction"])

        def _fake_send(tx):
            tx.state = "pending"

        with patch.object(tx_model, "_send_payment_request", _fake_send):
            self.assertTrue(self.sub1.create_payment(invoice))
        self.assertFalse(self.sub1.payment_exception)
        self.assertEqual(invoice.transaction_ids.state, "pending")
        # The "awaiting confirmation" note is posted by generate_invoice, not
        # create_payment, so a direct charge does not duplicate it.
        self.assertFalse(
            self.sub1.message_ids.filtered(
                lambda m: "awaiting confirmation" in (m.body or "")
            )
        )

    def test_payment_reference_falls_back_to_subscription(self):
        # Charge-before-post: the invoice is still draft (no sequence number),
        # so the payment reference must fall back to the subscription's own
        # reference instead of an opaque timestamp.
        provider = self._prepare_provider()
        sub = self.create_sub({"code": "AUTOPAYREF"})
        self.create_sub_line(sub)
        sub.payment_token_id = self._create_payment_token(self.partner, provider)
        invoice = sub.create_invoice()
        self.assertEqual(invoice.state, "draft")
        tx_model = type(self.env["payment.transaction"])

        def _fake_send(tx):
            tx.state = "pending"

        with patch.object(tx_model, "_send_payment_request", _fake_send):
            self.assertTrue(sub.create_payment(invoice))
        transaction = invoice.transaction_ids
        self.assertEqual(len(transaction), 1)
        self.assertIn("AUTOPAYREF", transaction.reference)

    def test_generate_invoice_auto_payment_pending_message(self):
        # While the charge is pending the invoice stays draft: post a single
        # clean "submitted; awaiting confirmation" note - no "Draft Invoice"
        # display name, no "To validate", no bare "False".
        provider = self._prepare_provider()
        template = self.create_sub_template(
            {"invoicing_mode": "invoice", "auto_create_payment": True}
        )
        sub = self.create_sub({"template_id": template.id})
        self.create_sub_line(sub)
        sub.payment_token_id = self._create_payment_token(self.partner, provider)
        tx_model = type(self.env["payment.transaction"])

        def _fake_send(tx):
            tx.state = "pending"

        with patch.object(tx_model, "_send_payment_request", _fake_send):
            sub.generate_invoice()
        invoice = sub.invoice_ids
        self.assertEqual(invoice.state, "draft")
        awaiting = sub.message_ids.filtered(
            lambda m: "awaiting confirmation" in (m.body or "")
        )
        self.assertEqual(len(awaiting), 1)
        self.assertNotIn("Draft Invoice", awaiting[0].body)
        self.assertNotIn("False", awaiting[0].body)
        self.assertFalse(
            sub.message_ids.filtered(lambda m: "To validate" in (m.body or ""))
        )

    def test_transaction_cancel_flags_subscription(self):
        # An accepted (pending) automatic payment that the provider later
        # cancels or reverses (permanent failure / chargeback) must surface on
        # the subscription: exception flag + to-do activity. Stage and next
        # invoice date are intentionally left untouched.
        provider = self._prepare_provider()
        template = self.create_sub_template(
            {"invoicing_mode": "invoice", "auto_create_payment": True}
        )
        sub = self.create_sub({"template_id": template.id})
        self.create_sub_line(sub)
        sub.payment_token_id = self._create_payment_token(self.partner, provider)
        invoice = sub.create_invoice()
        tx_model = type(self.env["payment.transaction"])

        def _fake_send(tx):
            tx.state = "pending"

        with patch.object(tx_model, "_send_payment_request", _fake_send):
            self.assertTrue(sub.create_payment(invoice))
        self.assertFalse(sub.payment_exception)
        stage_before = sub.stage_id
        next_date_before = sub.recurring_next_date
        # Provider cancels the transaction afterwards.
        invoice.transaction_ids._set_canceled()
        self.assertTrue(sub.payment_exception)
        self.assertTrue(
            sub.activity_ids.filtered(
                lambda a: a.summary == sub._payment_failure_activity_summary()
            )
        )
        # Stage and schedule are left as-is (posted invoice stands as the
        # receivable; the exception flag stops further auto-billing).
        self.assertEqual(sub.stage_id, stage_before)
        self.assertEqual(sub.recurring_next_date, next_date_before)

    def test_payment_declined(self):
        provider = self._prepare_provider()
        self.sub1.payment_token_id = self._create_payment_token(self.partner, provider)
        invoice = self._post_subscription_invoice(self.sub1)
        tx_model = type(self.env["payment.transaction"])

        def _fake_send(tx):
            tx.state = "error"

        with patch.object(tx_model, "_send_payment_request", _fake_send):
            self.assertFalse(self.sub1.create_payment(invoice))
        self.assertTrue(self.sub1.payment_exception)

    def test_payment_token_partner_constraint(self):
        provider = self._prepare_provider()
        token = self._create_payment_token(self.partner_2, provider)
        with self.assertRaises(exceptions.ValidationError):
            self.sub1.payment_token_id = token

    def test_onchange_suggest_token(self):
        template = self.create_sub_template(
            {"invoicing_mode": "invoice_send", "auto_create_payment": True}
        )
        provider = self._prepare_provider()
        token = self._create_payment_token(self.partner, provider)
        sub = self.env["sale.subscription"].new(
            {
                "template_id": template.id,
                "partner_id": self.partner.id,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        sub._onchange_partner_id_payment_token()
        self.assertEqual(sub.payment_token_id, token)

    def test_generate_invoice_auto_payment_no_token(self):
        template = self.create_sub_template(
            {"invoicing_mode": "invoice_send", "auto_create_payment": True}
        )
        sub = self.create_sub({"template_id": template.id})
        self.create_sub_line(sub)
        original_next_date = sub.recurring_next_date
        move_send = type(self.env["account.move.send"])
        with patch.object(
            move_send, "_generate_and_send_invoices", return_value=None
        ) as mock_send:
            sub.generate_invoice()
        mock_send.assert_not_called()
        self.assertTrue(sub.payment_exception)
        # Invoice is kept in draft (never posted) and the schedule is not
        # advanced, so the period is retried once the token is fixed.
        self.assertEqual(len(sub.invoice_ids), 1)
        self.assertEqual(sub.invoice_ids.state, "draft")
        self.assertEqual(sub.recurring_next_date, original_next_date)
        self.assertTrue(
            sub.activity_ids.filtered(
                lambda a: a.summary == sub._payment_failure_activity_summary()
            )
        )

    def test_auto_payment_reuses_failed_draft(self):
        template = self.create_sub_template(
            {"invoicing_mode": "invoice", "auto_create_payment": True}
        )
        sub = self.create_sub({"template_id": template.id})
        self.create_sub_line(sub)
        sub.generate_invoice()
        first_invoice = sub.invoice_ids
        self.assertEqual(len(first_invoice), 1)
        self.assertEqual(first_invoice.state, "draft")
        # Second run reuses the lingering failed draft instead of duplicating.
        sub.generate_invoice()
        self.assertEqual(sub.invoice_ids, first_invoice)

    def test_generate_invoice_auto_payment_success(self):
        provider = self._prepare_provider()
        template = self.create_sub_template(
            {"invoicing_mode": "invoice_send", "auto_create_payment": True}
        )
        sub = self.create_sub({"template_id": template.id})
        self.create_sub_line(sub)
        sub.payment_token_id = self._create_payment_token(self.partner, provider)
        original_next_date = sub.recurring_next_date
        tx_model = type(self.env["payment.transaction"])
        move_send = type(self.env["account.move.send"])

        def _fake_send(tx):
            tx._set_done()

        with (
            patch.object(tx_model, "_send_payment_request", _fake_send),
            patch.object(
                move_send, "_generate_and_send_invoices", return_value=None
            ) as mock_send,
        ):
            sub.generate_invoice()
        invoice = sub.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.state, "posted")
        self.assertIn(invoice.payment_state, ("in_payment", "paid"))
        mock_send.assert_called_once()
        self.assertFalse(sub.payment_exception)
        self.assertNotEqual(sub.recurring_next_date, original_next_date)
        # A settled charge posts a closing confirmation note with the real
        # invoice number, and leaves no dangling "awaiting confirmation".
        confirmation = sub.message_ids.filtered(
            lambda m: "Automatic payment confirmed for invoice" in (m.body or "")
            and invoice.name in (m.body or "")
        )
        self.assertEqual(len(confirmation), 1)
        self.assertFalse(
            sub.message_ids.filtered(
                lambda m: "awaiting confirmation" in (m.body or "")
            )
        )

    def test_generate_invoice_draft_mode_auto_payment_silent(self):
        provider = self._prepare_provider()
        template = self.create_sub_template(
            {"invoicing_mode": "draft", "auto_create_payment": True}
        )
        sub = self.create_sub({"template_id": template.id})
        self.create_sub_line(sub)
        sub.payment_token_id = self._create_payment_token(self.partner, provider)
        tx_model = type(self.env["payment.transaction"])
        move_send = type(self.env["account.move.send"])

        def _fake_send(tx):
            tx._set_done()

        with (
            patch.object(tx_model, "_send_payment_request", _fake_send),
            patch.object(
                move_send, "_generate_and_send_invoices", return_value=None
            ) as mock_send,
        ):
            sub.generate_invoice()
        # Draft mode + automatic payment: the paid invoice is posted but no
        # email is sent (silent background billing).
        self.assertEqual(sub.invoice_ids.state, "posted")
        mock_send.assert_not_called()
        self.assertFalse(sub.payment_exception)

    def test_generate_invoice_without_auto_payment_sends_email(self):
        template = self.create_sub_template({"invoicing_mode": "invoice_send"})
        sub = self.create_sub({"template_id": template.id})
        self.create_sub_line(sub)
        move_send = type(self.env["account.move.send"])
        with patch.object(
            move_send, "_generate_and_send_invoices", return_value=None
        ) as mock_send:
            sub.generate_invoice()
        mock_send.assert_called_once()
        self.assertFalse(sub.payment_exception)

    def test_cron_skips_payment_exception(self):
        template = self.create_sub_template(
            {"invoicing_mode": "invoice_send", "auto_create_payment": True}
        )
        sub = self.create_sub(
            {
                "template_id": template.id,
                "date_start": fields.Date.today() - relativedelta(days=10),
                "in_progress": True,
                "payment_exception": True,
            }
        )
        self.create_sub_line(sub)
        sub.recurring_next_date = fields.Date.today() - relativedelta(days=1)
        sub.cron_subscription_management()
        self.assertEqual(len(sub.invoice_ids), 0)

    def test_so_subscription_token_handoff(self):
        template = self.create_sub_template(
            {"invoicing_mode": "invoice_send", "auto_create_payment": True}
        )
        self.product_1.product_tmpl_id.write(
            {"subscribable": True, "subscription_template_id": template.id}
        )
        provider = self._prepare_provider()
        token = self._create_payment_token(self.partner, provider)
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_1.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        tx = self.env["payment.transaction"].create(
            {
                "provider_id": provider.id,
                "payment_method_id": token.payment_method_id.id,
                "token_id": token.id,
                "operation": "online_token",
                "reference": "SO-TEST-TOKEN",
                "amount": 100.0,
                "currency_id": so.currency_id.id,
                "partner_id": self.partner.id,
                "state": "done",
            }
        )
        so.transaction_ids = [Command.link(tx.id)]
        so.with_context(uid=1).action_confirm()
        subscription = so.subscription_ids
        self.assertEqual(len(subscription), 1)
        self.assertEqual(subscription.payment_token_id, token)

    def test_payment_no_journal_on_provider(self):
        provider = self._prepare_provider()
        provider.journal_id = False
        token = self._create_payment_token(self.partner, provider)
        self.sub1.payment_token_id = token
        invoice = self._post_subscription_invoice(self.sub1)
        self.assertFalse(self.sub1.create_payment(invoice))
        self.assertTrue(self.sub1.payment_exception)
        msgs = self.sub1.message_ids.filtered(
            lambda m: "no payment journal" in (m.body or "")
        )
        self.assertEqual(len(msgs), 1)

    def test_payment_send_request_raises(self):
        provider = self._prepare_provider()
        self.sub1.payment_token_id = self._create_payment_token(self.partner, provider)
        invoice = self._post_subscription_invoice(self.sub1)
        tx_model = type(self.env["payment.transaction"])

        def _raise(tx):
            raise RuntimeError("network error")

        with (
            patch.object(tx_model, "_send_payment_request", _raise),
            mute_logger("odoo.addons.subscription_oca.models.sale_subscription"),
        ):
            self.assertFalse(self.sub1.create_payment(invoice))
        self.assertTrue(self.sub1.payment_exception)
        msgs = self.sub1.message_ids.filtered(
            lambda m: "could not be sent" in (m.body or "")
        )
        self.assertEqual(len(msgs), 1)

    def test_generate_invoice_sale_and_invoice_auto_payment(self):
        provider = self._prepare_provider()
        template = self.create_sub_template(
            {"invoicing_mode": "sale_and_invoice", "auto_create_payment": True}
        )
        sub = self.create_sub({"template_id": template.id})
        self.create_sub_line(sub)
        sub.payment_token_id = self._create_payment_token(self.partner, provider)
        sub.sale_subscription_line_ids.mapped("product_id").write(
            {"invoice_policy": "order"}
        )
        tx_model = type(self.env["payment.transaction"])

        def _fake_send(tx):
            tx._set_done()

        with (
            patch.object(tx_model, "_send_payment_request", _fake_send),
            patch.object(tx_model, "_post_process", lambda tx: None),
        ):
            sub.generate_invoice()
        self.assertFalse(sub.payment_exception)

    def test_onchange_token_skips_when_auto_pay_off(self):
        template = self.create_sub_template({"invoicing_mode": "invoice_send"})
        provider = self._prepare_provider()
        token = self._create_payment_token(self.partner, provider)
        sub = self.env["sale.subscription"].new(
            {
                "template_id": template.id,
                "partner_id": self.partner.id,
                "payment_token_id": token.id,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        sub._onchange_partner_id_payment_token()
        self.assertEqual(sub.payment_token_id, token)

    def test_onchange_token_skips_when_token_matches_partner(self):
        template = self.create_sub_template(
            {"invoicing_mode": "invoice_send", "auto_create_payment": True}
        )
        provider = self._prepare_provider()
        token = self._create_payment_token(self.partner, provider)
        sub = self.env["sale.subscription"].new(
            {
                "template_id": template.id,
                "partner_id": self.partner.id,
                "payment_token_id": token.id,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        sub._onchange_partner_id_payment_token()
        self.assertEqual(sub.payment_token_id, token)
