# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AgreementType(models.Model):
    _inherit = "agreement.type"

    is_rebate = fields.Boolean(
        string="Is rebate agreement type",
    )
