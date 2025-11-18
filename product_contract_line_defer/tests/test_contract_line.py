# Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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

        # One line is deferred
        line1.enable_deferred()
        self.assertTrue(line1.is_deferred)

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
