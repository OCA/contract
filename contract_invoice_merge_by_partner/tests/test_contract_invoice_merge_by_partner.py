# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


class TestContractInvoiceMergeByPartner(common.SavepointCase):
    """ Use case : Prepare some data for current test case """
    @classmethod
    def setUpClass(cls):
        super(TestContractInvoiceMergeByPartner, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'customer': True,
            'name': "Test Customer",
            'contract_invoice_merge': True,
        })
        cls.uom = cls.env.ref('product.product_uom_hour')
        cls.product = cls.env['product.product'].create({
            'name': 'Custom Service',
            'type': 'service',
            'uom_id': cls.uom.id,
            'uom_po_id': cls.uom.id,
            'sale_ok': True,
        })
        cls.contract1 = cls.env['account.analytic.account'].create({
            'name': 'Test contract',
            'partner_id': cls.partner.id,
            'recurring_invoices': False,
        })

    def test_invoices_merged(self):
        res = self.env['account.analytic.account'].recurring_create_invoice()
        self.assertEqual(res, True)
        self.contract1.write({
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
        contracts = self.env['account.analytic.account'].search([
            ('partner_id', '=', self.partner.id)
        ])
        contracts.recurring_create_invoice()
        invoices = self.env['account.invoice'].search(
            [('partner_id', '=', self.partner.id)])
        inv_draft = invoices.filtered(lambda x: x.state == 'draft')
        self.assertEqual(len(inv_draft), 1)
        inv_cancel = invoices.filtered(lambda x: x.state == 'cancel')
        self.assertFalse(inv_cancel)
