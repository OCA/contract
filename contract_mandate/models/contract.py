# Copyright 2017 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    mandate_id = fields.Many2one(
        comodel_name="account.banking.mandate",
        ondelete="restrict",
        string="Direct Debit Mandate",
        help="If mandate required in payment method and not set mandate, "
        "invoice takes the first valid mandate",
        index=True,
        check_company=True,
        compute="_compute_mandate_id",
        store=True,
        readonly=False,
    )
    mandate_required = fields.Boolean(
        related="payment_mode_id.payment_method_id.mandate_required", readonly=True
    )
    commercial_partner_id = fields.Many2one(
        related="partner_id.commercial_partner_id",
        readonly=True,
        string="Commercial Entity",
    )

    @api.depends("payment_mode_id")
    def _compute_mandate_id(self):
        self.filtered(lambda rec: not rec.mandate_required).mandate_id = False

    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals = super()._prepare_invoice(date_invoice, journal=journal)
        if self.mandate_id:
            invoice_vals["mandate_id"] = self.mandate_id.id
        elif self.payment_mode_id.payment_method_id.mandate_required:
            mandate = self.env["account.banking.mandate"].search(
                [
                    ("partner_id", "=", self.partner_id.commercial_partner_id.id),
                    ("state", "=", "valid"),
                    ("company_id", "=", self.company_id.id),
                ],
                limit=1,
            )
            invoice_vals["mandate_id"] = mandate.id
        return invoice_vals
