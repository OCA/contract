# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    enable_contract_line_refund_on_stop = fields.Boolean(
        help="If enabled, users can stop a contract line even after it has been "
        "invoiced. A refund will automatically be created for the invoiced period "
        "beyond the stop date.",
    )
