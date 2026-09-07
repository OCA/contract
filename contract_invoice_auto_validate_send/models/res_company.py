# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    auto_send_contract_invoice = fields.Boolean(
        help="Send auto-validated contract invoices to the customer using their "
        "preferred method (email or Peppol).",
    )
    auto_send_author_partner_id = fields.Many2one(
        "res.partner",
        string="Auto-Send Invoice Author",
        compute="_compute_auto_send_author_partner_id",
        store=True,
        readonly=False,
        help="Partner recorded as the author when auto-sending contract "
        "invoices. Defaults to the company's own partner.",
    )

    @api.depends("partner_id")
    def _compute_auto_send_author_partner_id(self):
        for company in self:
            if not company.auto_send_author_partner_id:
                company.auto_send_author_partner_id = company.partner_id
