# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    defer_contract_line_start = fields.Boolean(
        "Defer contract line start",
        help="At creation, defer contract lines by default (i.e. do not invoice until "
        "activated). Use this setting if you sell contracts which start dates are "
        "unknown at the conclusion of the sale.",
    )
