# Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.contract.tests.test_contract import TestContractBase


class Test(BaseCommon, TestContractBase):
    """
    Tests for contract.line
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

    def _enable_default_setting(self):
        self.company.write({"defer_contract_line_start": True})

    def test_contract_line_defer(self):
        line1 = self.contract2.contract_line_ids
        line2 = line1.copy()
        self.assertEqual(len(self.contract2.contract_line_ids), 2)

        date_early = line1.recurring_next_date
        date_late = date_early + relativedelta(months=1)
        line2.recurring_next_date = date_late
        self.assertEqual(self.contract2.recurring_next_date, date_early)

        # One line is deferred
        line1.enable_deferred()
        self.assertTrue(line1.is_deferred)
        self.assertIn("Deferred - ", line1.display_name)
        self.assertFalse(line1.recurring_next_date)
        self.assertEqual(self.contract2.recurring_next_date, date_late)

        line1._check_recurring_next_date_recurring_invoices()

        # One line is invoiced
        self.contract2.recurring_create_invoice()
        invoice = self.contract2._get_related_invoices()
        self.assertNotIn(line1, invoice.invoice_line_ids.mapped("contract_line_id"))
        self.assertIn(line2, invoice.invoice_line_ids.mapped("contract_line_id"))

    def test_contract_line_deferred_default(self):
        self._enable_default_setting()
        contract_form = Form(self.contract)
        with contract_form.contract_line_ids.new() as contract_line_form:
            contract_line_form.product_id = self.product_1
            self.assertTrue(contract_line_form.is_deferred)

    def test_contract_line_deferred_disable(self):
        self._enable_default_setting()
        today = fields.date.today()
        line1 = self.contract2.contract_line_ids
        line1.date_start = today - relativedelta(days=5)
        line1.date_end = today - relativedelta(days=3)
        line1.enable_deferred()

        # Test onchange
        contract_line_form = Form(line1)
        contract_line_form.is_deferred = False
        self.assertEqual(contract_line_form.date_start, today)
        self.assertFalse(contract_line_form.date_end)

    def test_contract_line_deferred_disable_no_date_start(self):
        """Disabling defer with no date_start must not raise a TypeError."""
        self._enable_default_setting()
        today = fields.date.today()
        line1 = self.contract2.contract_line_ids
        line1.date_start = False
        line1.date_end = False
        line1.enable_deferred()

        contract_line_form = Form(line1)
        contract_line_form.is_deferred = False
        self.assertEqual(contract_line_form.date_start, today)
        self.assertFalse(contract_line_form.date_end)

    def test_compute_is_deferred_display_type(self):
        """A display type line must never be deferred."""
        line = self.contract2.contract_line_ids
        line.is_deferred = True
        self.assertTrue(line.is_deferred)
        line.display_type = "line_section"
        self.assertFalse(line.is_deferred)

    def test_compute_is_deferred_no_recompute_on_company_change(self):
        """Disabling the company setting must not un-defer already deferred lines."""
        line = self.contract2.contract_line_ids
        line.is_deferred = True
        self.assertTrue(line.is_deferred)
        self.company.defer_contract_line_start = False
        self.assertTrue(line.is_deferred)

    def test_contract_line_deferred_wizard(self):
        today = fields.date.today()
        tomorrow = today + relativedelta(days=1)
        line1 = self.contract2.contract_line_ids
        line1.enable_deferred()
        self.assertTrue(line1.is_deferred)
        action = self.env["ir.actions.actions"]._for_xml_id(
            "contract_line_defer.contract_line_activate_wizard_act_window"
        )
        action["context"] = {"default_contract_line_id": line1.id}
        wizard = Form.from_action(self.env, action)
        wizard.date_end = tomorrow
        wizard.save()
        wizard.record.activate_line()
        self.assertFalse(line1.is_deferred)
        self.assertEqual(line1.date_start, today)
        self.assertEqual(line1.date_end, tomorrow)
