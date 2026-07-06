# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    do_not_group_move = fields.Boolean(
        string="Do not group moves together",
        related="company_id.do_not_group_move",
        readonly=False,
    )
