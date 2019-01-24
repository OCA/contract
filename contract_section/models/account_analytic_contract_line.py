# Copyright 2018 Road-Support - Roel Adriaans
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticContractLine(models.Model):
    _inherit = 'account.analytic.contract.line'

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")],
        default=False,
        help="Technical field for UX purpose."
    )
