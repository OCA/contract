# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ContractRecurrencyBasicMixin(models.AbstractModel):

    _inherit = "contract.recurrency.basic.mixin"

    fixed_invoice_day_number = fields.Integer(
        default=0,
        help="Fill in this in order to generate an invoice with an invoice date "
        "at this day number. Set it to 0 to deactivate it.",
    )

    @api.constrains("fixed_invoice_day_number")
    def _check_fixed_invoice_date_number(self):
        for contract in self:
            if (
                contract.fixed_invoice_day_number > 31
                or contract.fixed_invoice_day_number < 0
            ):
                raise ValidationError(
                    _("The Fixed Invoice Date Number value should be between 0 and 31")
                )
