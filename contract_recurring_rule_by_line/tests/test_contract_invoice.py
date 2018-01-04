# -*- coding: utf-8 -*-
# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestContractInvoice(TransactionCase):
    # Use case : Prepare some data for current test case

    def setUp(self):
        super(TestContractInvoice, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        self.product = self.env.ref('product.product_product_2')
        self.product.taxes_id += self.env['account.tax'].search(
            [('type_tax_use', '=', 'sale')], limit=1)
        self.product.description_sale = 'Test description sale'
        self.contract = self.env['account.analytic.account'].create({
            'name': 'Test Contract',
            'partner_id': self.partner.id,
            'pricelist_id': self.partner.property_product_pricelist.id,
            'recurring_invoices': True,
            'date_start': '2016-02-15',
            'recurring_next_date': '2016-02-29',
            'recurring_rule_type': 'yearly',
            'recurring_interval': 1,
        })
        account_analytic_invoice_line_obj = self.env[
            'account.analytic.invoice.line']
        self.contract_line_1 = account_analytic_invoice_line_obj.create(
            {
                'analytic_account_id': self.contract.id,
                'product_id': self.product.id,
                'name': 'Services from #START# to #END#',
                'quantity': 1,
                'uom_id': self.product.uom_id.id,
                'price_unit': 100,
                'recurring_rule_type': 'yearly',
                'recurring_interval': 1,
            })
        self.contract_line_2 = account_analytic_invoice_line_obj.create(
            {
                'analytic_account_id': self.contract.id,
                'product_id': self.product.id,
                'name': 'Services from #START# to #END#',
                'quantity': 1,
                'uom_id': self.product.uom_id.id,
                'price_unit': 100,
                'recurring_rule_type': 'monthly',
                'recurring_interval': 1,
            })

    def test_contract(self):

        self.contract.recurring_create_invoice()
        self.invoices = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        # TODO
