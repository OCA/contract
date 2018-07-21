# Copyright 2016 Tecnativa - Carlos Dauden
# Copyright 2017 Tecnativa - Pedro M. Baeza
# Copyright 2018 Road-Support - Roel Adriaans
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestContractBase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestContractBase, cls).setUpClass()
        cls.partner = cls.env.ref('base.res_partner_2')
        cls.product = cls.env.ref('product.product_product_2')
        cls.product.taxes_id += cls.env['account.tax'].search(
            [('type_tax_use', '=', 'sale')], limit=1)
        cls.product.description_sale = 'Test description sale'
        cls.template_vals = {
            'recurring_rule_type': 'yearly',
            'recurring_interval': 12345,
            'name': 'Test Contract Template',
        }
        cls.template = cls.env['account.analytic.contract'].create(
            cls.template_vals,
        )
        cls.contract = cls.env['account.analytic.account'].create({
            'name': 'Test Contract',
            'partner_id': cls.partner.id,
            'pricelist_id': cls.partner.property_product_pricelist.id,
            'recurring_invoices': True,
            'date_start': '2016-02-15',
            'recurring_next_date': '2016-02-29',
        })
        cls.line_vals = {
            'analytic_account_id': cls.contract.id,
            'product_id': cls.product.id,
            'name': 'Services from #START# to #END#',
            'quantity': 1,
            'uom_id': cls.product.uom_id.id,
            'price_unit': 100,
            'discount': 50,
        }
        cls.acct_line = cls.env['account.analytic.invoice.line'].create(
            cls.line_vals,
        )


class TestContract(TestContractBase):
    def test_contract_default_name(self):
        """ Create invoice, based on default values.
        Should have a valid name"""
        self.contract.cron_recurring_create_invoice()
        invoice_id = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        self.assertEqual(invoice_id.invoice_line_ids.name,
                         'Services from 02/29/2016 to 03/28/2016')

    def test_contract_computed_name(self):
        """ Create invoice, based on computed values.
        Should have these computed values in invoice line."""
        self.acct_line.unlink()
        self.line_vals['name'] = "Services from #START(dd/MM/yyyy)# " \
                                 "to #END(d MMMM yy)#"
        self.acct_line = self.env['account.analytic.invoice.line'].create(
            self.line_vals,
        )
        self.contract.cron_recurring_create_invoice()
        invoice_id = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        self.assertEqual(invoice_id.invoice_line_ids.name,
                         'Services from 29/02/2016 to 28 March 16')

    def test_contract_computed_broken_name(self):
        """ Broken date format. Should not give an error, but empty
        test in the invoice line."""
        self.acct_line.unlink()
        self.line_vals['name'] = "Services from #START(Invalid)# " \
                                 "to #END(EEEE dd MMMM yyy)#"
        self.acct_line = self.env['account.analytic.invoice.line'].create(
            self.line_vals,
        )
        self.contract.cron_recurring_create_invoice()
        invoice_id = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        self.assertEqual(invoice_id.invoice_line_ids.name,
                         'Services from  to Monday 28 March 2016')
