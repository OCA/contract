# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = 'res.company'

    specific_contract_payment_mode = fields.Boolean(
        string="Specific payment mode for contracts created from sale orders"
    )
