# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon

to_date = fields.Date.to_date


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
                "min_term_renewal_interval": 12,
                "min_term_renewal_rule_type": "monthly",
                "min_term_notice_interval": 3,
                "min_term_notice_rule_type": "monthly",
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
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create({"product_id": product.id}) for product in products
                ],
            }
        )

    def test_product_minimum_term_excludes_auto_renew(self):
        with self.assertRaises(ValidationError):
            self.product_min_term.is_auto_renew = True
        product_form = Form(self.product_fixed.product_tmpl_id)
        product_form.is_auto_renew = True
        product_form.contract_duration_type = "minimum_term"
        self.assertFalse(product_form.is_auto_renew)

    def test_sale_order_line_minimum_term(self):
        line = self._create_order(self.product_min_term).order_line
        self.assertEqual(line.contract_duration_type, "minimum_term")
        self.assertEqual(line.min_term_interval, 24)
        self.assertEqual(line.min_term_renewal_interval, 12)
        self.assertEqual(line.min_term_notice_interval, 3)
        self.assertEqual(line.date_start, to_date("2026-09-18"))
        self.assertFalse(line.date_end)
        self.assertFalse(line.is_auto_renew)
        with self.assertRaises(ValidationError):
            line.is_auto_renew = True

    def test_sale_order_line_fixed(self):
        line = self._create_order(self.product_fixed).order_line
        self.assertEqual(line.contract_duration_type, "fixed")
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
        self.assertEqual(line_min_term.min_term_renewal_interval, 12)
        self.assertEqual(line_min_term.min_term_notice_interval, 3)
        self.assertFalse(line_min_term.date_end)
        self.assertFalse(line_min_term.is_auto_renew)
        self.assertEqual(line_min_term.min_term_date_end, to_date("2028-09-17"))
        self.assertEqual(line_min_term.min_term_notice_date, to_date("2028-06-17"))
        line_fixed = contract.contract_line_ids - line_min_term
        self.assertEqual(line_fixed.date_end, to_date("2027-09-17"))
        self.assertFalse(line_fixed.min_term_interval)
        self.assertFalse(line_fixed.min_term_date_end)
        self.assertEqual(contract.min_term_date_end, to_date("2028-09-17"))

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
