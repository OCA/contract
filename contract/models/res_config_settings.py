# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    create_new_line_at_contract_line_renew = fields.Boolean(
        related="company_id.create_new_line_at_contract_line_renew",
        readonly=False,
        string="Create New Line At Contract Line Renew",
        help="If checked, a new line will be generated at contract line renew "
        "and linked to the original one as successor. The default "
        "behavior is to extend the end date of the contract by a new "
        "subscription period",
    )
