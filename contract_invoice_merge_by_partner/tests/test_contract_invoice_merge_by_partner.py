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
            'taxes_id': [(6, 0, [])],
        })
        cls.contract1 = cls.env['account.analytic.account'].create({
            'name': 'Test contract',
            'partner_id': cls.partner.id,
            'recurring_invoices': False,
        })

    def test_invoices_merged(self):
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
        contract2 = self.contract1.copy()
        contract3 = self.contract1.copy()
        contract4 = self.contract1.copy()
        contracts = self.contract1 + contract2 + contract3 + contract4
        invoice = contracts.recurring_create_invoice()
        self.assertEqual(len(invoice), 1)
        self.assertEqual(len(invoice.invoice_line_ids), 4)
