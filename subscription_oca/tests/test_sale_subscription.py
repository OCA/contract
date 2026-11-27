# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.product.tests.common import ProductCommon

LOGGER = "odoo.addons.subscription_oca.models.sale_subscription"


class TestSaleSubscription(ProductCommon, BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Cron pl"})
        cls.product = cls._create_product(
            name="Cron product",
            lst_price=100.0,
            subscribable=True,
            uom_id=cls.uom_unit.id,
            taxes_id=[(6, 0, [])],
        )
        cls.template = cls.env["sale.subscription.template"].create(
            {
                "name": "Cron template",
                "code": "CRN",
                "recurring_rule_type": "months",
                "recurring_interval": 1,
                "invoicing_mode": "draft",
            }
        )
        Stage = cls.env["sale.subscription.stage"]
        cls.stage_pre = Stage.search([("type", "=", "pre")], limit=1) or Stage.create(
            {"name": "Cron pre", "type": "pre"}
        )
        cls.stage_in_progress = Stage.search(
            [("type", "=", "in_progress")], limit=1
        ) or Stage.create({"name": "Cron in progress", "type": "in_progress"})

    def _new_subscription(self, name, stage, next_date):
        partner = self.env["res.partner"].create({"name": name})
        subscription = self.env["sale.subscription"].create(
            {
                "partner_id": partner.id,
                "template_id": self.template.id,
                "pricelist_id": self.pricelist.id,
                "date_start": fields.Date.today(),
            }
        )
        self.env["sale.subscription.line"].create(
            {
                "sale_subscription_id": subscription.id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "price_unit": 100.0,
                "tax_ids": [(6, 0, [])],
            }
        )
        # write() of an in_progress stage recomputes the next date: set it after
        subscription.stage_id = stage
        subscription.recurring_next_date = next_date
        return subscription

    def _invoices(self, subscription):
        return self.env["account.move"].search(
            [("subscription_id", "=", subscription.id)]
        )

    def _patch_db_error(self, failing):
        """generate_invoice creates the invoice and then hits a DB error
        for ``failing``, which aborts the transaction like a real
        constraint violation would."""
        SaleSubscription = type(self.env["sale.subscription"])
        original = SaleSubscription.generate_invoice

        def side_effect(subscription):
            original(subscription)
            if subscription.id in failing.ids:
                subscription.env.cr.execute("SELECT 1/0")

        return patch.object(
            SaleSubscription,
            "generate_invoice",
            autospec=True,
            side_effect=side_effect,
        )

    @mute_logger("odoo.sql_db")
    def test_cron_db_error_in_progress_does_not_block_others(self):
        today = fields.Date.today()
        # The failing one is processed first (ordered by recurring_next_date)
        bad_date = today - relativedelta(days=2)
        good_date = today - relativedelta(days=1)
        bad = self._new_subscription("Bad", self.stage_in_progress, bad_date)
        good = self._new_subscription("Good", self.stage_in_progress, good_date)

        with self._patch_db_error(bad), self.assertLogs(LOGGER, level="ERROR"):
            self.env["sale.subscription"].cron_subscription_management()

        # The failing subscription is fully rolled back: no invoice, same date
        self.assertFalse(self._invoices(bad))
        self.assertEqual(bad.recurring_next_date, bad_date)
        # The other one is invoiced and its next date advanced
        self.assertEqual(len(self._invoices(good)), 1)
        self.assertGreater(good.recurring_next_date, good_date)

    @mute_logger("odoo.sql_db")
    def test_cron_db_error_on_start_does_not_block_others(self):
        today = fields.Date.today()
        bad = self._new_subscription(
            "Bad start", self.stage_pre, today - relativedelta(days=1)
        )
        good = self._new_subscription("Good start", self.stage_pre, today)

        with self._patch_db_error(bad), self.assertLogs(LOGGER, level="ERROR"):
            self.env["sale.subscription"].cron_subscription_management()

        # The failing start is rolled back: still "pre", not started, no invoice
        self.assertEqual(bad.stage_id, self.stage_pre)
        self.assertFalse(bad.in_progress)
        self.assertFalse(self._invoices(bad))
        # The other one is started and invoiced
        self.assertEqual(good.stage_id.type, "in_progress")
        self.assertTrue(good.in_progress)
        self.assertEqual(len(self._invoices(good)), 1)
