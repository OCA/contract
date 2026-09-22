# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    def compute_prorated(self, period_first_date, period_last_date, invoice_date):
        self.ensure_one()
        return self._compute_prorated(
            period_first_date,
            period_last_date,
            invoice_date,
            self.recurring_rule_type,
            self.recurring_interval,
            self.recurring_invoicing_type,
        )

    @api.model
    def _compute_prorated(
        self,
        period_first_date,
        period_last_date,
        invoice_date,
        recurring_rule_type,
        recurring_interval,
        recurring_invoicing_type,
    ):
        def _invoiced_days(next_date, last_date):
            return (next_date - last_date).days + 1

        relative_delta = self.get_relative_delta(
            recurring_rule_type, recurring_interval
        )
        theoretical_next_date = invoice_date
        if (
            recurring_rule_type == "monthlylastday"
            and recurring_invoicing_type == "post-paid"
        ):
            relative_delta = self.get_relative_delta("monthly", recurring_interval)
            theoretical_next_date += self.get_relative_delta("daily", 1)

        if recurring_invoicing_type == "pre-paid":
            theoretical_next_date += relative_delta
        theoretical_last_date = theoretical_next_date - relative_delta
        theoretical_next_date -= self.get_relative_delta("daily", 1)
        real_last_date = period_first_date
        real_next_date = period_last_date
        return _invoiced_days(real_next_date, real_last_date) / _invoiced_days(
            theoretical_next_date, theoretical_last_date
        )
