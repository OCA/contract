# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    auto_send_contract_invoice = fields.Boolean(
        help="Send auto-validated contract invoices to the customer using their "
        "preferred method (email or Peppol).",
    )
