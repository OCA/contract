# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import calendar

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ContractContract(models.Model):

    _inherit = "contract.contract"

    next_fixed_invoice_date = fields.Date(
        compute="_compute_next_fixed_invoice_date",
        readonly=True,
    )

    @api.constrains("fixed_invoice_day_number")
    def _check_fixed_invoice_date_number(self):
        for contract in self:
            if (
                contract.fixed_invoice_day_number > 31
                or contract.fixed_invoice_day_number < 1
            ):
                raise ValidationError(
                    _("The Fixed Invoice Date Number value should be between 1 and 31")
                )

    def _recurring_create_invoice(self, date_ref=False):
        moves = self.env["account.move"].browse()
        if not date_ref:
            for date, contracts in self.partition("next_fixed_invoice_date").items():
                moves |= super(ContractContract, contracts)._recurring_create_invoice(
                    date_ref=date
                )
        return moves

    @api.depends("recurring_next_date", "fixed_invoice_day_number")
    def _compute_next_fixed_invoice_date(self):
        # Partition the contracts per recurring next date and day number
        for dates, contracts in self.partition(
            lambda c: (c.recurring_next_date, c.fixed_invoice_day_number)
        ).items():
            recurring_next_date = dates[0]
            next_day = dates[1]
            if next_day:
                if recurring_next_date.day > next_day:
                    recurring_next_date = recurring_next_date + relativedelta(months=1)
                max_day = calendar.monthrange(
                    year=recurring_next_date.year, month=recurring_next_date.month
                )[1]
                next_day = min(max_day, next_day)
                next_fixed_date = recurring_next_date.replace(day=next_day)
                contracts.next_fixed_invoice_date = next_fixed_date
            else:
                contracts.next_fixed_invoice_date = False
