from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        string="Payment Mode",
        domain=[("payment_type", "=", "inbound")],
        index=True,
    )

    @api.onchange("partner_id")
    def on_change_partner_id(self):
        self.payment_mode_id = self.partner_id.customer_payment_mode_id.id

    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals, move_form = super()._prepare_invoice(
            date_invoice=date_invoice, journal=journal
        )
        if self.payment_mode_id:
            invoice_vals["payment_mode_id"] = self.payment_mode_id.id
        return invoice_vals, move_form
