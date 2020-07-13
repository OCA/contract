# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    create_new_line_at_contract_line_renew = fields.Boolean(
        string="Create New Line At Contract Line Renew",
        help="If checked, a new line will be generated at contract line renew "
        "and linked to the original one as successor. The default "
        "behavior is to extend the end date of the contract by a new "
        "subscription period",
    )
