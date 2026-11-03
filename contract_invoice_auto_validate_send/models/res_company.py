# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    auto_send_contract_invoice = fields.Boolean(
        compute="_compute_auto_send_contract_invoice",
        store=True,
        readonly=False,
        help="Send auto-validated contract invoices to the customer using their "
        "preferred method (email or Peppol).",
    )

    @api.depends("auto_post_contract_invoice")
    def _compute_auto_send_contract_invoice(self):
        for company in self:
            if not company.auto_post_contract_invoice:
                company.auto_send_contract_invoice = False
