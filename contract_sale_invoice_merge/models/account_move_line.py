# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    origin = fields.Char(
        readonly=True,
        tracking=True,
        copy=False,
        help="The document(s) that generated the invoice line.",
    )
