# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ContractRecurrencyBasicMixin(models.AbstractModel):

    _inherit = "contract.recurrency.basic.mixin"

    fixed_invoice_day_number = fields.Integer(
        help="Fill in this in order to generate an invoice with an invoice date "
        "at this day number."
    )
