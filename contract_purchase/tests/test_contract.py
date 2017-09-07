# -*- coding: utf-8 -*-
# © 2017 Stefan Becker <s.becker@humanilog.org>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.exceptions import ValidationError
from openerp.tests.common import SavepointCase

class TestContract(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestContract, cls).setUpClass()

        cls.partner = cls.env.ref('base.res_partner_2')

        cls.product = cls.env.ref('product.product_product_2')
        cls.product.description_sale = 'Test description sale'

        cls.purchase_journal = cls.env['account.journal'].create({
            'name': 'Purchase Journal',
            'type': 'purchase',
            'company_id': cls.env.user.company_id.id,
            'code': '1337'
        })

        contract = cls.env['account.analytic.account'].new({
            'name': 'Test Contract',
            'type': 'purchase',
            'company_id': cls.env.user.company_id.id,
            'partner_id': cls.partner.id,
            'pricelist_id': cls.partner.property_product_pricelist.id,
            'recurring_invoices': True,
            'date_start': '2016-02-15',
            'recurring_next_date': '2016-02-29',
        })
        contract.onchange_type()
        cls.contract = cls.env['account.analytic.account'].create(
            contract._convert_to_write(contract._cache))

        cls.contract_line = cls.env['account.analytic.invoice.line'].create({
            'analytic_account_id': cls.contract.id,
            'product_id': cls.product.id,
            'name': 'Services from #START# to #END#',
            'quantity': 1,
            'uom_id': cls.product.uom_id.id,
            'price_unit': 100,
            'discount': 50,
        })

    def test_contract(self):
        self.assertEqual(self.contract.journal_id, self.purchase_journal)

        new_invoice = self.contract.recurring_create_invoice()
        self.assertEqual(new_invoice.type, 'in_invoice')
