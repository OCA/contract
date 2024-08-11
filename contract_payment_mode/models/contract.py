from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        string="Payment Mode",
        domain=[("payment_type", "=", "inbound")],
        index=True,
        compute="_compute_payment_mode_id",
        store=True,
        readonly=False,
    )

    @api.depends("partner_id", "contract_type")
    def _compute_payment_mode_id(self):
        for rec in self:
            partner = rec.with_company(rec.company_id).partner_id
            if rec.contract_type == "purchase":
                rec.payment_mode_id = partner.supplier_payment_mode_id.id
            else:
                rec.payment_mode_id = partner.customer_payment_mode_id.id

    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals = super()._prepare_invoice(
            date_invoice=date_invoice, journal=journal
        )
        if self.payment_mode_id:
            invoice_vals["payment_mode_id"] = self.payment_mode_id.id
        return invoice_vals
