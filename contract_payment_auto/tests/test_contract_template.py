# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestContractTemplate(TransactionCase):

    def setUp(self):
        super(TestContractTemplate, self).setUp()
        self.Model = self.env['contract.template']

    def test_default_invoice_mail_template_id(self):
        """ It should return a mail template associated with invoice. """
        res = self.Model._default_invoice_mail_template_id()
        self.assertEqual(
            res.model, 'account.invoice',
        )

    def test_default_pay_retry_mail_template_id(self):
        """ It should return a mail template associated with invoice. """
        res = self.Model._default_pay_retry_mail_template_id()
        self.assertEqual(
            res.model, 'account.invoice',
        )

    def test_default_pay_fail_mail_template_id(self):
        """ It should return a mail template associated with invoice. """
        res = self.Model._default_pay_fail_mail_template_id()
        self.assertEqual(
            res.model, 'account.invoice',
        )

    def test_default_auto_pay_retries(self):
        """ It should return an int. """
        self.assertIsInstance(
            self.Model._default_auto_pay_retries(), int,
        )

    def test_default_auto_pay_retry_hours(self):
        """ It should return an int. """
        self.assertIsInstance(
            self.Model._default_auto_pay_retry_hours(), int,
        )

    def test_context_mail_templates(self):
        """ It should return a dict. """
        self.assertIsInstance(
            self.Model._context_mail_templates(), dict,
        )
