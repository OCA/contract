# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractTemplateLine(models.Model):
    # Fields declared here are inherited by contract.line as well.
    _inherit = "contract.template.line"

    show_details = fields.Boolean(default=True)
    show_section_subtotal = fields.Boolean(
        default=True,
        help="Uncheck this if you want to hide the subtotal on section part",
    )
    show_subtotal = fields.Boolean(default=True)
    show_line_amount = fields.Boolean(default=True)
