# Copyright 2023 ooops404
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import uuid
from unittest.mock import patch

from dateutil.relativedelta import relativedelta

from odoo import exceptions, fields
from odoo.tests import TransactionCase
from odoo.tools import mute_logger


class TestSubscriptionOCA(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.portal_user = cls.env.ref("base.demo_user0")
        if not cls.env.company.chart_template_id:
            # Load a CoA if there's none in current company
            coa = cls.env.ref("l10n_generic_coa.configurable_chart_template", False)
            if not coa:
                # Load the first available CoA
                coa = cls.env["account.chart.template"].search(
                    [("visible", "=", True)], limit=1
                )
            coa.try_loading(company=cls.env.company, install_demo=False)
        cls.cash_journal = cls.env["account.journal"].search(
            [
                ("type", "=", "cash"),
                ("company_id", "=", cls.env.ref("base.main_company").id),
            ]
        )[0]
        cls.sale_journal = cls.env["account.journal"].search(
            [
                ("type", "=", "sale"),
                ("company_id", "=", cls.env.ref("base.main_company").id),
            ]
        )[0]
        cls.pricelist1 = cls.env["product.pricelist"].create(
            {
                "name": "pricelist for contract test",
            }
        )
        cls.pricelist2 = cls.env["product.pricelist"].create(
            {
                "name": "pricelist for contract test 2",
                "discount_policy": "with_discount",
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
                "price_include": True,
            }
        )
        cls.product_1 = cls.env.ref("product.product_product_1")
        cls.product_1.subscribable = True
        cls.product_1.taxes_id = [(6, 0, cls.tax_10pc_incl.ids)]
        cls.product_2 = cls.env.ref("product.product_product_2")
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
        cls.pricelist_default = cls.env.ref("product.list0")
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
            "product_ids": [(6, 0, [cls.product_1.id, cls.product_2.id])],
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
            "tag_ids": [(6, 0, [cls.tag.id])],
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
        so.with_context(uid=1).action_confirm()  # without subs.

    def test_subscription_oca_sub_lines(self):
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

    @patch(
        "odoo.addons.subscription_oca.models.sale_subscription."
        "SaleSubscription.generate_invoice"
    )
    def test_subscription_oca_sub_cron_error(self, generate_invoice_patch):
        # Simulate something failing in generating an invoice,
        # we expect something being logged
        generate_invoice_patch.side_effect = exceptions.UserError("Error")
        with mute_logger("odoo.addons.subscription_oca.models.sale_subscription"):
            with self.assertRaises(exceptions.UserError):
                self.sub1.cron_subscription_management()

    def test_subscription_oca_sub_cron(self):
        # sale.subscription
        self.sub1.cron_subscription_management()
        # invoice should be created by cron
        inv_id = self.env["account.move"].search(
            [("subscription_id", "=", self.sub1.id)]
        )
        self.assertEqual(len(inv_id), 1)
        self.assertEqual(self.sub1.recurring_total, 27.95)
        self.assertEqual(self.sub1.amount_total, 30.75)
        self.assertEqual(self.sub2.recurring_total, 66.2)
        self.assertEqual(self.sub2.amount_total, 69)

    def test_subscription_oca_sub1_workflow(self):
        res = self._collect_all_sub_test_results(self.sub1)
        self.assertTrue(res[0])
        self.assertTrue(res[1])
        self.assertEqual(res[3], 2)
        self.assertEqual(res[4], 2 * 30.75)
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
        self.assertEqual(1, len(subscription.invoice_ids.filtered("is_move_sent")))
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
        self.sub_line.sale_subscription_id.pricelist_id.discount_policy = (
            "without_discount"
        )
        self.sub_line.product_uom_qty = 100
        self.env.user.groups_id = [
            (4, self.env.ref("product.group_discount_per_so_line").id)
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
        self.pricelist_l3.discount_policy = "without_discount"
        self.pricelist_l3.currency_id = self.env.ref("base.THB")
        self.sub_line.sale_subscription_id.pricelist_id = self.pricelist_l3
        res = self.sub_line._get_display_price(self.product_1)
        self.assertAlmostEqual(int(res), 514)
        self.sub_line.product_uom_qty = 300
        res = self.sub_line.read(["discount"])
        self.assertEqual(res[0]["discount"], 0)

    def test_compute_display_name(self):
        stage = self.env["sale.subscription.stage"].create(
            {
                "name": "Test Stage",
                "type": "pre",
            }
        )
        self.assertEqual(stage.display_name, "Test Stage", "display_name not computed")
        stage.name = "Updated Test Stage"
        stage._compute_display_name()
        self.assertEqual(
            stage.display_name, "Updated Test Stage", "display_name not computed"
        )

    def test_open_subscription(self):
        invoice = self.sub1.create_invoice()
        action = invoice.action_open_subscription()
        self.assertEqual(action["domain"], [("id", "=", self.sub1.id)])

    def _collect_all_sub_test_results(self, subscription):
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
        # self.assertEqual(len(inv_ids), 2)
        # self.assertEqual(sum(inv_ids.mapped("amount_total")), 2 * 30.75)
        # self.assertEqual(subscription.account_invoice_ids_count, 2)
        test_res.append(len(inv_ids))
        test_res.append(sum(inv_ids.mapped("amount_total")))
        test_res.append(subscription.account_invoice_ids_count)
        res = subscription.action_view_account_invoice_ids()
        # self.assertEqual(res["type"], "ir.actions.act_window")
        # self.assertEqual(subscription.sale_order_ids_count, 1)
        test_res.append(res["type"])
        test_res.append(subscription.sale_order_ids_count)
        subscription.action_view_sale_order_ids()
        # self.assertIn(str(subscription.sale_order_ids.id), str(res["domain"]))
        test_res.append(subscription.sale_order_ids.id)
        subscription.calculate_recurring_next_date(fields.Datetime.now())
        # self.assertEqual(
        #     subscription.recurring_next_date,
        #     fields.Date.today() + relativedelta(months=1),
        # )
        test_res.append(subscription.recurring_next_date)
        subscription.partner_id = self.partner_2
        subscription.onchange_partner_id()
        # self.assertEqual(
        #     subscription.pricelist_id.id, self.partner_2.property_product_pricelist.id
        # )
        test_res.append(subscription.pricelist_id.id)
        subscription.onchange_partner_id_fpos()
        # self.assertFalse(subscription.fiscal_position_id)
        test_res.append(subscription.fiscal_position_id)
        res = subscription.action_close_subscription()
        self.assertEqual(res["type"], "ir.actions.act_window")
        test_res.append(res["type"])
        group_stage_ids = subscription._read_group_stage_ids(
            stages=self.env["sale.subscription.stage"].search([]), domain=[], order="id"
        )
        test_res.append(group_stage_ids)
        return test_res
