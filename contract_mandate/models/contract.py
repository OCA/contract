# Copyright 2017 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    mandate_id = fields.Many2one(
        comodel_name='account.banking.mandate',
        ondelete='restrict',
        string='Direct Debit Mandate',
        help="If mandate required in payment method and not set mandate, "
             "invoice takes the first valid mandate",
        index=True,
    )
    mandate_required = fields.Boolean(
        related='payment_mode_id.payment_method_id.mandate_required',
        readonly=True)
    commercial_partner_id = fields.Many2one(
        related='partner_id.commercial_partner_id',
        readonly=True,
        string='Commercial Entity',
    )

    @api.multi
    @api.onchange('payment_mode_id')
    def _onchange_payment_mode_id(self):
        self.ensure_one()
        if not self.mandate_required:
            self.mandate_id = False

    @api.multi
    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals = super(ContractContract, self)._prepare_invoice(
            date_invoice, journal=journal
        )
        if self.mandate_id:
            invoice_vals['mandate_id'] = self.mandate_id.id
        elif self.payment_mode_id.payment_method_id.mandate_required:
            mandate = self.env['account.banking.mandate'].search([
                ('partner_id', '=', self.partner_id.commercial_partner_id.id),
                ('state', '=', 'valid'),
            ], limit=1)
            invoice_vals['mandate_id'] = mandate.id
        return invoice_vals

    @api.model
    def _finalize_invoice_creation(self, invoices):
        """
        This override preserves the contract when calling the partner's
        onchange.
        """
        mandates_by_invoice = {}
        for invoice in invoices:
            mandates_by_invoice[invoice] = invoice.mandate_id
        res = super(ContractContract, self)._finalize_invoice_creation(
            invoices)
        for invoice in invoices:
            invoice.mandate_id = mandates_by_invoice.get(invoice)
        return res
