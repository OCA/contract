# Copyright 2016 Tecnativa - Carlos Dauden
# Copyright 2017 Tecnativa - Pedro M. Baeza
# Copyright 2018 Roel Adriaans - roel@road-support.nl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContract(TestContractBase):
    @classmethod
    def setUpClass(cls):
        # Reuse the tests from the contract module, but replace the
        # contract line
        super(TestContract, cls).setUpClass()
        cls.acct_line.unlink()
        cls.section = cls.env.ref('sale.sale_layout_cat_2')
        cls.line_vals.update({
            'layout_category_id': cls.section.id,
        })
        cls.acct_line = cls.env['account.analytic.invoice.line'].create(
            cls.line_vals,
        )

    def test_create_invoice(self):
        """ Create contract with section"""
        self.assertTrue(self.acct_line.layout_category_id)
        self.contract.recurring_create_invoice()
        invoice_id = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        self.assertEqual(invoice_id.invoice_line_ids.layout_category_id.id,
                         self.line_vals['layout_category_id'])
