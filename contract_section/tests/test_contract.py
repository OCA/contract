# Copyright 2016 Tecnativa - Carlos Dauden
# Copyright 2017 Tecnativa - Pedro M. Baeza
# Copyright 2018 Roel Adriaans - roel@road-support.nl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestContractBase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestContractBase, cls).setUpClass()
        cls.section = cls.env.ref('sale.sale_layout_cat_2')
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
            'layout_category_id': cls.section.id,
        }
        cls.acct_line = cls.env['account.analytic.invoice.line'].create(
            cls.line_vals,
        )


class TestContract(TestContractBase):
    def test_create_invoice(self):
        """ Create contract with section"""
        self.assertTrue(self.acct_line.layout_category_id)
        self.contract.recurring_create_invoice()
        invoice_id = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        self.assertEqual(invoice_id.invoice_line_ids.layout_category_id.id,
                         self.line_vals['layout_category_id'])
