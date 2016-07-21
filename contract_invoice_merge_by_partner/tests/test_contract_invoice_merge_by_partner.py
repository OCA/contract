# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestContractInvoiceMergeByPartner(TransactionCase):
    """ Use case : Prepare some data for current test case """
    def setUp(self):
        super(TestContractInvoiceMergeByPartner, self).setUp()
        self.partner = self.env['res.partner'].create({
            'customer': True,
            'name': "Test Customer",
            'contract_invoice_merge': True,
        })
        self.product = self.env.ref('product.product_product_consultant')
        self.uom = self.env.ref('product.product_uom_hour')
        self.contract1 = self.env['account.analytic.account'].create({
            'name': 'Test contract',
            'partner_id': self.partner.id,
            'type': 'contract',
            'recurring_invoices': True,
            'recurring_rule_type': 'monthly',
            'recurring_interval': 1,
            'recurring_invoice_line_ids': [
                (0, 0, {'quantity': 2.0,
                        'price_unit': 100.0,
                        'name': self.product.name,
                        'product_id': self.product.id,
                        'uom_id': self.uom.id})],
        })
        self.contract2 = self.contract1.copy()
        self.contract3 = self.contract1.copy()
        self.contract4 = self.contract1.copy()

    def test_invoices_merged(self):
        self.env['account.analytic.account']._recurring_create_invoice()
        invoices = self.env['account.invoice'].search(
            [('partner_id', '=', self.partner.id)])
        inv_draft = invoices.filtered(lambda x: x.state == 'draft')
        self.assertEqual(len(inv_draft), 1)
        inv_cancel = invoices.filtered(lambda x: x.state == 'cancel')
        self.assertFalse(inv_cancel)
