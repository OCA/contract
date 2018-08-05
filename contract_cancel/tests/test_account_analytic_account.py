# -*- coding: utf-8 -*-
# Copyright 2018 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import random
from datetime import timedelta, date
from mock import patch

from odoo.tests.common import TransactionCase


MOCK_RECURRING = 'odoo.addons.contract.models.account_analytic_account.' \
                 'AccountAnalyticAccount.recurring_create_invoice'


class TestAccountAnalyticAccount(TransactionCase):

    def setUp(self):
        super(TestAccountAnalyticAccount, self).setUp()

        self.AnalyticAccount = self.env['account.analytic.account']
        self.Account = self.env['account.account']
        self.Invoice = self.env['account.invoice']

        self.today = date.today()
        self.future = self.today + timedelta(days=10)
        self.past = self.today - timedelta(days=10)

        self.contract_1 = self._create_contract()
        self.account_1 = self.Account.search([], limit=1)

    def _create_contract(self, update_vals=None):
        vals = {
            'name': '%s' % random.randint(1, 1000),
            'auto_cancel_contract': True,
            'partner_id': self.env.user.partner_id.id,
            'recurring_invoices': True,
        }
        if update_vals:
            vals.update(update_vals)
        return self.AnalyticAccount.create(vals)

    def _create_invoice(self, update_vals=None):
        vals = {
            'contract_id': self.contract_1.id,
            'date_due': self.past,
            'account_id': self.account_1.id,
            'partner_id': self.env.user.partner_id.id,
            'user_id': self.env.user.id,
        }
        if update_vals:
            vals.update(update_vals)
        return self.Invoice.create(vals)

    def test_compute_past_due_invoice_ids_one(self):
        """ It should include 1 of 2 invoice """
        self._create_invoice({'date_due': self.future})
        invoice_2 = self._create_invoice()
        self.assertEquals(
            [invoice_2.id],
            self.contract_1.past_due_invoice_ids.ids,
        )

    def test_compute_past_due_invoice_ids_none(self):
        """ It should not include any invoices """
        self._create_invoice({'date_due': self.future})
        self.assertFalse(
            self.contract_1.past_due_invoice_ids,
        )

    def test_compute_past_due_invoice_ids_both(self):
        """ It should include both invoices """
        self._create_invoice()
        self._create_invoice()
        self.assertEquals(
            len(self.contract_1.past_due_invoice_ids),
            2,
        )

    @patch(MOCK_RECURRING)
    def test_recurring_create_invoice_one(self, mock_recurring):
        """ Super should be called with one contract """
        contract_2 = self._create_contract()
        # Past due invoice created for self.contract_1
        self._create_invoice()
        recs = contract_2 + self.contract_1
        recs.recurring_create_invoice()
        self.assertTrue(
            contract_2.recurring_invoices,
        )
        self.assertFalse(
            self.contract_1.recurring_invoices,
        )
        mock_recurring.assert_called_once()

    @patch(MOCK_RECURRING)
    def test_recurring_create_invoice_none(self, mock_recurring):
        """ Super should not be called """
        self._create_invoice()
        self.contract_1.recurring_create_invoice()
        self.assertFalse(
            self.contract_1.recurring_invoices,
        )
        mock_recurring.assert_not_called()

    @patch(MOCK_RECURRING)
    def test_recurring_create_invoice_contract_cancel(self, mock_recurring):
        """ Super should not be called as contract_cancel False """
        self.contract_1.auto_cancel_contract = False
        self._create_invoice()
        self.contract_1.recurring_create_invoice()
        self.assertTrue(
            self.contract_1.recurring_invoices,
        )
        mock_recurring.assert_called_once()

    @patch(MOCK_RECURRING)
    def test_recurring_create_invoice_both(self, mock_recurring):
        """ Super should be called with both contract """
        contract_2 = self._create_contract()
        # Past due invoice created for self.contract_1
        self._create_invoice({
            'date_due': self.future,
        })
        self._create_invoice({
            'contract_id': contract_2.id,
            'date_due': self.future,
        })
        recs = contract_2 + self.contract_1
        recs.recurring_create_invoice()
        self.assertTrue(
            contract_2.recurring_invoices,
        )
        self.assertTrue(
            self.contract_1.recurring_invoices,
        )
        mock_recurring.assert_called_once()
