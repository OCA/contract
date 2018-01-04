# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


def _context_mail_templates(env):
    return env['account.analytic.contract']._context_mail_templates()


class AccountAnalyticContract(models.Model):
    _inherit = 'account.analytic.contract'

    invoice_mail_template_id = fields.Many2one(
        string='Invoice Message',
        comodel_name='mail.template',
        default=lambda s: s._default_invoice_mail_template_id(),
        domain="[('model', '=', 'account.invoice')]",
        context=_context_mail_templates,
        help="During the automatic payment process, an invoice will be "
             "created and validated. If this template is selected, it will "
             "automatically be sent to the customer during this process "
             "using the defined template.",
    )
    pay_retry_mail_template_id = fields.Many2one(
        string='Payment Retry Message',
        comodel_name='mail.template',
        default=lambda s: s._default_pay_retry_mail_template_id(),
        domain="[('model', '=', 'account.invoice')]",
        context=_context_mail_templates,
        help="If automatic payment fails for some reason, but will be "
             "re-attempted later, this message  will be sent to the billed "
             "partner.",
    )
    pay_fail_mail_template_id = fields.Many2one(
        string='Payment Failed Message',
        comodel_name='mail.template',
        default=lambda s: s._default_pay_fail_mail_template_id(),
        domain="[('model', '=', 'account.invoice')]",
        context=_context_mail_templates,
        help="If automatic payment fails for some reason, this message "
             "will be sent to the billed partner.",
    )
    is_auto_pay = fields.Boolean(
        string='Auto Pay?',
        default=True,
        help="Check this to enable automatic payment for invoices that are "
             "created for this contract.",
    )
    auto_pay_retries = fields.Integer(
        default=lambda s: s._default_auto_pay_retries(),
        help="Amount times to retry failed/declined automatic payment "
             "before giving up."
    )
    auto_pay_retry_hours = fields.Integer(
        default=lambda s: s._default_auto_pay_retry_hours(),
        help="Amount of hours that should lapse until a failed automatic "
             "is retried.",
    )

    @api.model
    def _default_invoice_mail_template_id(self):
        return self.env.ref(
            'account.email_template_edi_invoice',
            raise_if_not_found=False,
        )

    @api.model
    def _default_pay_retry_mail_template_id(self):
        return self.env.ref(
            'contract_payment_auto.mail_template_auto_pay_retry',
            raise_if_not_found=False,
        )

    @api.model
    def _default_pay_fail_mail_template_id(self):
        return self.env.ref(
            'contract_payment_auto.mail_template_auto_pay_fail',
            raise_if_not_found=False,
        )

    @api.model
    def _default_auto_pay_retries(self):
        return 3

    @api.model
    def _default_auto_pay_retry_hours(self):
        return 24

    @api.model
    def _context_mail_templates(self):
        """ Return a context for use in mail templates. """
        default_model = self.env.ref('account.model_account_invoice')
        report_template = self.env.ref('account.account_invoices')
        return {
            'default_model_id': default_model.id,
            'default_email_from': "${(object.user_id.email and '%s <%s>' % "
                                  "(object.user_id.name, object.user_id.email)"
                                  " or '')|safe}",
            'default_partner_to': '${object.partner_id.id}',
            'default_lang': '${object.partner_id.lang}',
            'default_auto_delete': True,
            'report_template': report_template.id,
            'report_name': "Invoice_${(object.number or '').replace('/','_')}"
                           "_${object.state == 'draft' and 'draft' or ''}",

        }
