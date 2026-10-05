# Copyright 2025 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    @api.depends(
        "next_period_date_start",
        "recurring_invoicing_type",
        "recurring_invoicing_offset",
        "recurring_rule_type",
        "recurring_interval",
        "date_end",
        "recurring_next_date",
        "align_billing_cycle",
    )
    def _compute_next_period_date_end(self):
        for rec in self:
            rec.next_period_date_end = self.get_next_period_date_end(
                rec.next_period_date_start,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
                next_invoice_date=rec.recurring_next_date,
                recurring_invoicing_type=rec.recurring_invoicing_type,
                recurring_invoicing_offset=rec.recurring_invoicing_offset,
                align_billing_cycle=rec.align_billing_cycle,
            )

    @api.depends(
        "next_period_date_start",
        "recurring_invoicing_type",
        "recurring_invoicing_offset",
        "recurring_rule_type",
        "recurring_interval",
        "date_end",
        "contract_line_ids.recurring_next_date",
        "contract_line_ids.is_canceled",
        "align_billing_cycle",
    )
    def _compute_recurring_next_date(self):
        for contract in self:
            recurring_next_date = contract.contract_line_ids.filtered(
                lambda line: (
                    line.recurring_next_date
                    and not line.is_canceled
                    and (not line.display_type or line.is_recurring_note)
                )
            ).mapped("recurring_next_date")
            if (
                contract._origin
                and contract._origin.date_start != contract.date_start
                or not recurring_next_date
            ):
                contract.recurring_next_date = self.get_next_invoice_date(
                    contract.next_period_date_start,
                    contract.recurring_invoicing_type,
                    contract.recurring_invoicing_offset,
                    contract.recurring_rule_type,
                    contract.recurring_interval,
                    max_date_end=contract.date_end,
                    align_billing_cycle=contract.align_billing_cycle,
                )
            else:
                contract.recurring_next_date = min(recurring_next_date)
