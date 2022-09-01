# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from datetime import datetime, timedelta

from odoo import api, fields, models, _


_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = 'contract.contract'

    payment_token_id = fields.Many2one(
        string='Payment Token',
        comodel_name='payment.token',
        domain="[('partner_id', '=', partner_id)]",
        context="{'default_partner_id': partner_id}",
        help='This is the payment token that will be used to automatically '
             'reconcile debts against this account. If none is set, the '
             'bill to partner\'s default token will be used.',
    )

    @api.multi
    @api.onchange('partner_id')
    def _onchange_partner_id_payment_token(self):
        """ Clear the payment token when the partner is changed. """
        self.payment_token_id = self.env['payment.token']

    @api.model
    def cron_retry_auto_pay(self):
        """ Retry automatic payments for appropriate invoices. """

        invoice_lines = self.env['account.invoice.line'].search([
            ('invoice_id.state', '=', 'open'),
            ('invoice_id.auto_pay_attempts', '>', 0),
            ('contract_line_id.contract_id.is_auto_pay', '=', True),
        ])
        now = datetime.now()

        for invoice_line in invoice_lines:

            contract = invoice_line.contract_line_id.contract_id
            invoice = invoice_line.invoice_id
            fail_time = invoice.auto_pay_failed
            retry_delta = timedelta(hours=contract.auto_pay_retry_hours)
            retry_time = fail_time + retry_delta

            if retry_time < now:
                contract._do_auto_pay(invoice)

    @api.multi
    def _recurring_create_invoice(self, date_ref=False):
        """ If automatic payment is enabled, perform auto pay actions. """
        invoices = super(Contract, self)._recurring_create_invoice(date_ref)
        for invoice in invoices:
            contract = invoice.mapped(
                "invoice_line_ids.contract_line_id.contract_id")
            contract = contract and contract[0]
            if contract and contract.is_auto_pay:
                contract._do_auto_pay(invoice)
        return invoices

    @api.multi
    def _do_auto_pay(self, invoice):
        """ Perform all automatic payment operations on open invoices. """
        self.ensure_one()
        invoice.ensure_one()
        invoice.action_invoice_open()
        self._send_invoice_message(invoice)
        self._pay_invoice(invoice)

    @api.multi
    def _pay_invoice(self, invoice):
        """ Pay the invoice using the account or partner token. """

        if invoice.state != 'open':
            _logger.info('Cannot pay an invoice that is not in open state.')
            return

        if not invoice.residual:
            _logger.debug('Cannot pay an invoice with no balance.')
            return

        token = self.payment_token_id or self.partner_id.payment_token_id
        if not token:
            _logger.debug(
                'Cannot pay an invoice without defining a payment token',
            )
            return

        transaction = self.env['payment.transaction'].create(
            self._get_tx_vals(invoice, token),
        )
        valid_states = ['authorized', 'done']

        try:
            result = transaction.s2s_do_transaction()
            if not result or transaction.state not in valid_states:
                _logger.debug(
                    'Payment transaction failed (%s)',
                    transaction.state_message,
                )
            else:
                # Success
                return True

        except Exception:
            _logger.exception(
                'Payment transaction (%s) generated a gateway error.',
                transaction.id,
            )

        transaction.state = 'error'
        invoice.write({
            'auto_pay_attempts': invoice.auto_pay_attempts + 1,
            'auto_pay_failed': fields.Datetime.now(),
        })

        if invoice.auto_pay_attempts >= self.auto_pay_retries:
            template = self.pay_fail_mail_template_id
            self.write({
                'is_auto_pay': False,
                'payment_token_id': False,
            })
            if token == self.partner_id.payment_token_id:
                self.partner_id.payment_token_id = False

        else:
            template = self.pay_retry_mail_template_id

        if template:
            template.send_mail(invoice.id)

        return

    @api.multi
    def _get_tx_vals(self, invoice, token):
        """ Return values for creation of a payment.transaction for invoice. """
        amount_due = invoice.residual
        partner = token.partner_id
        reference = self.env['payment.transaction']._compute_reference({
            "invoice_ids": invoice.ids,
        })
        return {
            'reference': '%s' % reference,
            'acquirer_id': token.acquirer_id.id,
            'payment_token_id': token.id,
            'invoice_ids': [(4, invoice.id)],
            'amount': amount_due,
            'state': 'draft',
            'currency_id': invoice.currency_id.id,
            'partner_id': partner.id,
            'partner_country_id': partner.country_id.id,
            'partner_city': partner.city,
            'partner_zip': partner.zip,
            'partner_email': partner.email,
        }

    @api.multi
    def _send_invoice_message(self, invoice):
        """ Send the appropriate emails for the invoices if needed. """
        if invoice.sent:
            return
        if not self.invoice_mail_template_id:
            return
        _logger.info('Sending invoice %s, %s (template %s)',
                     invoice, invoice.number, self.invoice_mail_template_id)
        mail_id = self.invoice_mail_template_id.send_mail(invoice.id)
        invoice.with_context(mail_post_autofollow=True)
        invoice.sent = True
        invoice.message_post(body=_("Invoice sent"))
        return self.env['mail.mail'].browse(mail_id)
