from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    payment_mode_id = fields.Many2one(
        comodel_name='account.payment.mode',
        string='Payment Mode',
        domain=[('payment_type', '=', 'inbound')],
        index=True,
    )

    @api.onchange('partner_id')
    def on_change_partner_id(self):
        self.payment_mode_id = self.partner_id.customer_payment_mode_id.id

    @api.multi
    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals = super(ContractContract, self)._prepare_invoice(
            date_invoice=date_invoice, journal=journal)
        if self.payment_mode_id:
            invoice_vals['payment_mode_id'] = self.payment_mode_id.id
            invoice = self.env['account.invoice'].new(invoice_vals)
            invoice._onchange_payment_mode_id()
            invoice_vals = invoice._convert_to_write(invoice._cache)
        return invoice_vals

    @api.model
    def _finalize_invoice_creation(self, invoices):
        """
        This override preserves the payment mode when calling the partner's
        onchange.
        """
        payment_modes_by_invoice = {}
        for invoice in invoices:
            payment_modes_by_invoice[invoice] = invoice.payment_mode_id
        res = super(ContractContract, self)._finalize_invoice_creation(
            invoices)
        for invoice in invoices:
            invoice.payment_mode_id = payment_modes_by_invoice.get(invoice)
        return res
