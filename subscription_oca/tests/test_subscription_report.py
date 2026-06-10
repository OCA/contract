# Copyright 2026 Domatix - Alvaro Domatix
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.product.tests.common import ProductCommon


class TestSubscriptionReport(ProductCommon, BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Report pricelist"}
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Report partner",
                "property_product_pricelist": cls.pricelist.id,
            }
        )
        cls.product = cls._create_product(
            name="Report product",
            lst_price=120.0,
            subscribable=True,
            uom_id=cls.uom_unit.id,
            taxes_id=[(6, 0, [])],
        )
        cls.template = cls.env["sale.subscription.template"].create(
            {
                "name": "Report template",
                "code": "REP-MTH",
                "recurring_rule_type": "months",
                "recurring_interval": 1,
            }
        )
        cls.subscription = cls.env["sale.subscription"].create(
            {
                "partner_id": cls.partner.id,
                "template_id": cls.template.id,
                "pricelist_id": cls.pricelist.id,
                "date_start": fields.Date.today(),
            }
        )
        cls.line = cls.env["sale.subscription.line"].create(
            {
                "sale_subscription_id": cls.subscription.id,
                "product_id": cls.product.id,
                "product_uom_qty": 2.0,
                "price_unit": 120.0,
                "tax_ids": [(6, 0, [])],
            }
        )

    def _report_rows(self):
        self.env.flush_all()
        return self.env["sale.subscription.report"].search(
            [("subscription_id", "=", self.subscription.id)]
        )

    def test_report_has_one_row_per_line(self):
        rows = self._report_rows()
        self.assertEqual(len(rows), len(self.subscription.sale_subscription_line_ids))

    def test_report_row_matches_line_revenue(self):
        row = self._report_rows()
        self.assertAlmostEqual(row.recurring_monthly, self.line.recurring_monthly, 2)
        self.assertAlmostEqual(
            row.recurring_yearly, self.line.recurring_monthly * 12.0, 2
        )
        self.assertEqual(row.partner_id, self.partner)
        self.assertEqual(row.template_id, self.template)
        self.assertEqual(row.product_id, self.product)
        self.assertEqual(row.stage_type, self.subscription.stage_id.type)

    def test_report_mrr_aggregation_matches_subscription(self):
        self.env["sale.subscription.line"].create(
            {
                "sale_subscription_id": self.subscription.id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "price_unit": 60.0,
                "tax_ids": [(6, 0, [])],
            }
        )
        rows = self._report_rows()
        self.assertAlmostEqual(
            sum(rows.mapped("recurring_monthly")),
            self.subscription.recurring_monthly,
            2,
        )

    def test_report_excludes_archived_subscription(self):
        self.assertTrue(self._report_rows())
        self.subscription.active = False
        self.assertFalse(self._report_rows())
