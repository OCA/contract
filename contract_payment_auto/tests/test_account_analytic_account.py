# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock

from contextlib import contextmanager

from odoo import fields
from odoo.tools import mute_logger
from odoo.tests import common

from ..models import account_analytic_account


@common.at_install(False)
@common.post_install(True)
class TestAccountAnalyticAccount(common.HttpCase):
    def setUp(self):
        super(TestAccountAnalyticAccount, self).setUp()
        self.Model = self.env['account.analytic.account']
        self.partner = self.env.ref('base.res_partner_2')
        self.product = self.env.ref('product.product_product_2')
        self.product.taxes_id += self.env['account.tax'].search(
            [('type_tax_use', '=', 'sale')], limit=1)
        self.product.description_sale = 'Test description sale'
        self.template_vals = {
            'recurring_rule_type': 'yearly',
            'recurring_interval': 12345,
            'name': 'Test Contract Template',
            'is_auto_pay': True,
        }
        self.template = self.env['account.analytic.contract'].create(
            self.template_vals,
        )
        self.acquirer = self.env['payment.acquirer'].create({
            'name': 'Test Acquirer',
            'provider': 'manual',
            'view_template_id': self.env['ir.ui.view'].search([], limit=1).id,
        })
        self.payment_token = self.env['payment.token'].create({
            'name': 'Test Token',
            'partner_id': self.partner.id,
            'active': True,
            'acquirer_id': self.acquirer.id,
            'acquirer_ref': 'Test',
        })
        self.contract = self.Model.create({
            'name': 'Test Contract',
            'partner_id': self.partner.id,
            'pricelist_id': self.partner.property_product_pricelist.id,
            'recurring_invoices': True,
            'date_start': '2016-02-15',
            'recurring_next_date': fields.Datetime.now(),
            'payment_token_id': self.payment_token.id,
        })
        self.contract_line = self.env['account.analytic.invoice.line'].create({
            'analytic_account_id': self.contract.id,
            'product_id': self.product.id,
            'name': 'Services from #START# to #END#',
            'quantity': 1,
            'uom_id': self.product.uom_id.id,
            'price_unit': 100,
            'discount': 50,
        })

    def _validate_invoice(self, invoice):
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice._name, 'account.invoice')

    def _create_invoice(self, open=False, sent=False):
        self.contract.is_auto_pay = False
        invoice = self.contract._create_invoice()
        if open or sent:
            invoice.action_invoice_open()
        if sent:
            invoice.sent = True
        self.contract.is_auto_pay = True
        return invoice

    @contextmanager
    def _mock_transaction(self, state='authorized', s2s_side_effect=None):

        Transactions = self.contract.env['payment.transaction']
        TransactionsCreate = Transactions.create

        if not callable(s2s_side_effect):
            s2s_side_effect = [s2s_side_effect]

        s2s = mock.MagicMock()
        s2s.side_effect = s2s_side_effect

        def create(vals):
            record = TransactionsCreate(vals)
            record.state = state
            return record

        model_create = mock.MagicMock()
        model_create.side_effect = create

        Transactions._patch_method('create', model_create)
        Transactions._patch_method('s2s_do_transaction', s2s)

        try:
            yield
        finally:
            Transactions._revert_method('create')
            Transactions._revert_method('s2s_do_transaction')

    def test_onchange_partner_id_payment_token(self):
        """ It should clear the payment token. """
        self.assertTrue(self.contract.payment_token_id)
        self.contract._onchange_partner_id_payment_token()
        self.assertFalse(self.contract.payment_token_id)

    def test_create_invoice_no_autopay(self):
        """ It should return the new invoice without calling autopay. """
        self.contract.is_auto_pay = False
        with mock.patch.object(self.contract, '_do_auto_pay') as method:
            invoice = self.contract._create_invoice()
            self._validate_invoice(invoice)
            method.assert_not_called()

    def test_create_invoice_autopay(self):
        """ It should return the new invoice after calling autopay. """
        with mock.patch.object(self.contract, '_do_auto_pay') as method:
            invoice = self.contract._create_invoice()
            self._validate_invoice(invoice)
            method.assert_called_once_with(invoice)

    def test_do_auto_pay_ensure_one(self):
        """ It should ensure_one on self. """
        with self.assertRaises(ValueError):
            self.env['account.analytic.account']._do_auto_pay(
                self._create_invoice(),
            )

    def test_do_auto_pay_invoice_ensure_one(self):
        """ It should ensure_one on the invoice. """
        with self.assertRaises(ValueError):
            self.contract._do_auto_pay(
                self.env['account.invoice'],
            )

    def test_do_auto_pay_open_invoice(self):
        """ It should open the invoice. """
        invoice = self._create_invoice()
        self.contract._do_auto_pay(invoice)
        self.assertEqual(invoice.state, 'open')

    def test_do_auto_pay_sends_message(self):
        """ It should call the send message method with the invoice. """
        with mock.patch.object(self.contract, '_send_invoice_message') as m:
            invoice = self._create_invoice()
            self.contract._do_auto_pay(invoice)
            m.assert_called_once_with(invoice)

    def test_do_auto_pay_does_pay(self):
        """ It should try to pay the invoice. """
        with mock.patch.object(self.contract, '_pay_invoice') as m:
            invoice = self._create_invoice()
            self.contract._do_auto_pay(invoice)
            m.assert_called_once_with(invoice)

    def test_pay_invoice_not_open(self):
        """ It should return None if the invoice isn't open. """
        invoice = self._create_invoice()
        res = self.contract._pay_invoice(invoice)
        self.assertIs(res, None)

    def test_pay_invoice_no_residual(self):
        """ It should return None if no residual on the invoice. """
        invoice = self._create_invoice()
        invoice.state = 'open'
        res = self.contract._pay_invoice(invoice)
        self.assertIs(res, None)

    def test_pay_invoice_no_token(self):
        """ It should return None if no payment token. """
        self.contract.payment_token_id = False
        invoice = self._create_invoice(True)
        res = self.contract._pay_invoice(invoice)
        self.assertIs(res, None)

    def test_pay_invoice_success(self):
        """ It should return True on success. """
        with self._mock_transaction(s2s_side_effect=True):
            invoice = self._create_invoice(True)
            res = self.contract._pay_invoice(invoice)
            self.assertTrue(res)

    @mute_logger(account_analytic_account.__name__)
    def test_pay_invoice_exception(self):
        """ It should catch exceptions. """
        with self._mock_transaction(s2s_side_effect=Exception):
            invoice = self._create_invoice(True)
            res = self.contract._pay_invoice(invoice)
            self.assertIs(res, None)

    def test_pay_invoice_invalid_state(self):
        """ It should return None on invalid state. """
        with self._mock_transaction(s2s_side_effect=True):
            invoice = self._create_invoice(True)
            invoice.state = 'draft'
            res = self.contract._pay_invoice(invoice)
            self.assertIs(res, None)

    @mute_logger(account_analytic_account.__name__)
    def test_pay_invoice_increments_retries(self):
        """ It should increment invoice retries on failure. """
        with self._mock_transaction(s2s_side_effect=False):
            invoice = self._create_invoice(True)
            self.assertFalse(invoice.auto_pay_attempts)
            self.contract._pay_invoice(invoice)
            self.assertTrue(invoice.auto_pay_attempts)

    def test_pay_invoice_updates_fail_date(self):
        """ It should update the invoice auto pay fail date on failure. """
        with self._mock_transaction(s2s_side_effect=False):
            invoice = self._create_invoice(True)
            self.assertFalse(invoice.auto_pay_failed)
            self.contract._pay_invoice(invoice)
            self.assertTrue(invoice.auto_pay_failed)

    def test_pay_invoice_too_many_attempts(self):
        """ It should clear autopay after too many attempts. """
        with self._mock_transaction(s2s_side_effect=False):
            invoice = self._create_invoice(True)
            invoice.auto_pay_attempts = self.contract.auto_pay_retries - 1
            self.contract._pay_invoice(invoice)
            self.assertFalse(self.contract.is_auto_pay)
            self.assertFalse(self.contract.payment_token_id)

    def test_pay_invoice_too_many_attempts_partner_token(self):
        """ It should clear the partner token when attempts were on it. """
        self.partner.payment_token_id = self.contract.payment_token_id
        with self._mock_transaction(s2s_side_effect=False):
            invoice = self._create_invoice(True)
            invoice.auto_pay_attempts = self.contract.auto_pay_retries
            self.contract._pay_invoice(invoice)
            self.assertFalse(self.partner.payment_token_id)

    def test_get_tx_vals(self):
        """ It should return a dict. """
        self.assertIsInstance(
            self.contract._get_tx_vals(self._create_invoice()),
            dict,
        )

    def test_send_invoice_message_sent(self):
        """ It should return None if the invoice has already been sent. """
        invoice = self._create_invoice(sent=True)
        res = self.contract._send_invoice_message(invoice)
        self.assertIs(res, None)

    def test_send_invoice_message_no_template(self):
        """ It should return None if the invoice isn't sent. """
        invoice = self._create_invoice(True)
        self.contract.invoice_mail_template_id = False
        res = self.contract._send_invoice_message(invoice)
        self.assertIs(res, None)

    def test_send_invoice_message_sets_invoice_state(self):
        """ It should set the invoice to sent. """
        invoice = self._create_invoice(True)
        self.assertFalse(invoice.sent)
        self.contract._send_invoice_message(invoice)
        self.assertTrue(invoice.sent)

    def test_send_invoice_message_returns_mail(self):
        """ It should create and return the message. """
        invoice = self._create_invoice(True)
        res = self.contract._send_invoice_message(invoice)
        self.assertEqual(res._name, 'mail.mail')

    def test_cron_retry_auto_pay_needed(self):
        """ It should auto-pay the correct invoice if needed. """
        invoice = self._create_invoice(True)
        invoice.write({
            'auto_pay_attempts': 1,
            'auto_pay_failed': '2015-01-01 00:00:00',
        })
        meth = mock.MagicMock()
        self.contract._patch_method('_do_auto_pay', meth)
        try:
            self.contract.cron_retry_auto_pay()
        finally:
            self.contract._revert_method('_do_auto_pay')
        meth.assert_called_once_with(invoice)

    def test_cron_retry_auto_pay_skip(self):
        """ It should skip invoices that don't need to be paid. """
        invoice = self._create_invoice(True)
        invoice.write({
            'auto_pay_attempts': 1,
            'auto_pay_failed': fields.Datetime.now(),
        })
        meth = mock.MagicMock()
        self.contract._patch_method('_do_auto_pay', meth)
        try:
            self.contract.cron_retry_auto_pay()
        finally:
            self.contract._revert_method('_do_auto_pay')
        meth.assert_not_called()
