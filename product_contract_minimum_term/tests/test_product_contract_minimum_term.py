# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo import fields
from odoo.tests import Form, tagged

from odoo.addons.base.tests.common import BaseCommon

to_date = fields.Date.to_date


@tagged("post_install", "-at_install")
@freeze_time("2026-09-18")
class TestProductContractMinimumTerm(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Customer"})
        cls.contract_template = cls.env["contract.template"].create(
            {
                "name": "Template",
                # A fixed duration never gets the minimum term of the template
                "min_term_interval": 36,
            }
        )
        cls.product_min_term = cls.env["product.product"].create(
            {
                "name": "Internet 100",
                "type": "service",
                "list_price": 30,
                "is_contract": True,
                "property_contract_template_id": cls.contract_template.id,
                "contract_duration_type": "minimum_term",
                "min_term_interval": 24,
                "min_term_rule_type": "monthly",
                # The renewal of the minimum term and the notice reuse the
                # fields of product_contract
                "is_auto_renew": True,
                "auto_renew_interval": 12,
                "auto_renew_rule_type": "monthly",
                "termination_notice_interval": 3,
                "termination_notice_rule_type": "monthly",
            }
        )
        cls.product_fixed = cls.env["product.product"].create(
            {
                "name": "Router rental",
                "type": "service",
                "list_price": 5,
                "is_contract": True,
                "property_contract_template_id": cls.contract_template.id,
                "contract_duration_type": "fixed",
                "recurrence_number": 12,
                "recurrence_interval": "monthly",
            }
        )

    def _create_order(self, *products):
        """Like the user does it: the values of the product reach the line
        through the onchange, not through a plain create.
        """
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner
        for product in products:
            with order_form.order_line.new() as line:
                line.product_id = product
        return order_form.save()

    def test_sale_order_line_minimum_term(self):
        line = self._create_order(self.product_min_term).order_line
        self.assertEqual(line.contract_duration_type, "minimum_term")
        self.assertEqual(line.min_term_interval, 24)
        self.assertEqual(line.min_term_rule_type, "monthly")
        self.assertEqual(line.date_start, to_date("2026-09-18"))
        # Open-ended: "Auto Renew" renews the minimum term, not an end date
        self.assertFalse(line.date_end)
        self.assertTrue(line.is_auto_renew)
        self.assertEqual(line.auto_renew_interval, 12)

    def test_sale_order_line_fixed(self):
        line = self._create_order(self.product_fixed).order_line
        self.assertEqual(line.contract_duration_type, "fixed")
        self.assertFalse(line.min_term_interval)
        self.assertEqual(line.date_end, to_date("2027-09-17"))
        # Switching to a minimum term removes the end date
        line.contract_duration_type = "minimum_term"
        self.assertFalse(line.date_end)

    def test_contract_from_sale_order(self):
        order = self._create_order(self.product_min_term, self.product_fixed)
        order.action_confirm()
        contract = order.order_line.contract_id
        self.assertEqual(len(contract), 1)
        line_min_term = contract.contract_line_ids.filtered(
            lambda line: line.product_id == self.product_min_term
        )
        self.assertEqual(line_min_term.min_term_interval, 24)
        self.assertFalse(line_min_term.date_end)
        self.assertTrue(line_min_term.is_auto_renew)
        self.assertEqual(line_min_term.auto_renew_interval, 12)
        self.assertEqual(line_min_term.termination_notice_interval, 3)
        self.assertEqual(line_min_term.min_term_date_end, to_date("2028-09-17"))
        self.assertEqual(line_min_term.min_term_notice_date, to_date("2028-06-17"))
        line_fixed = contract.contract_line_ids - line_min_term
        self.assertEqual(line_fixed.date_end, to_date("2027-09-17"))
        self.assertFalse(line_fixed.min_term_interval)
        self.assertFalse(line_fixed.min_term_date_end)
        self.assertEqual(contract.min_term_date_end, to_date("2028-09-17"))
        # Only the line with a minimum term restricts the termination
        self.assertEqual(contract._get_min_term_lines(), line_min_term)

    def test_configurator(self):
        wizard = self.env["product.contract.configurator"].create(
            {"product_id": self.product_min_term.id}
        )
        self.assertEqual(wizard.contract_duration_type, "minimum_term")
        self.assertEqual(wizard.min_term_interval, 24)
        self.assertFalse(wizard.date_end)
        wizard = self.env["product.contract.configurator"].create(
            {"product_id": self.product_fixed.id}
        )
        self.assertEqual(wizard.contract_duration_type, "fixed")
        self.assertFalse(wizard.min_term_interval)
        self.assertEqual(wizard.date_end, to_date("2027-09-17"))
