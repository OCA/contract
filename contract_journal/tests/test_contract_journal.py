# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


class TestContractJournal(common.TransactionCase):

    def setUp(self):
        super(TestContractJournal, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        self.product = self.env.ref('product.product_product_2')
        self.journal = self.env['account.journal'].search(limit=1)
        self.product.description_sale = 'Test description sale'
        self.contract = self.env['account.analytic.account'].create({
            'name': 'Test Contract',
            'partner_id': self.partner.id,
            'pricelist_id': self.partner.property_product_pricelist.id,
            'recurring_invoices': True,
            'date_start': '2016-02-15',
            'recurring_next_date': '2016-02-29',
            'journal_id': self.journal.id,
        })

    def test_prepare_invoice(self):
        """ It should inject the journal into invoice vals """
        res = self.contract._prepare_invoice()
        self.assertEqual(res['journal_id'], self.journal.id)

    def test_default_journal_company(self):
        """ It should return journal of correct company """
        res = self.env['acount.analytic.account']._default_journal_id()
        self.assertEqual(res.company_id, self.env.user.company_id)

    def test_default_journal_type(self):
        """ It should return journal of correct type """
        res = self.env['acount.analytic.account']._default_journal_id()
        self.assertEqual(res.type, 'sale')

    def test_default_journal_context(self):
        """ It should return journal for correct company context """
        company = self.env['res.company'].create({'name': 'Test Inc.'})
        self.journal.write({
            'company_id': company.id,
            'type': 'sale',
        })
        Account = self.env['acount.analytic.account'].with_context(
            company_id=company.id,
        )
        res = Account._default_journal_id()
        self.assertEqual(res, self.journal)
