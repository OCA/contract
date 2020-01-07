# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.addons.queue_job.job import job

QUEUE_CHANNEL = "root.CONTRACT_FORECAST"


class ContractLine(models.Model):

    _inherit = "contract.line"

    forecast_period_ids = fields.One2many(
        comodel_name="contract.line.forecast.period",
        inverse_name="contract_line_id",
        string="Forecast Periods",
        required=False,
    )

    @api.multi
    def _prepare_contract_line_forecast_period(
        self, period_date_start, period_date_end, recurring_next_date
    ):
        self.ensure_one()
        return {
            "name": self._insert_markers(period_date_start, period_date_end),
            "contract_id": self.contract_id.id,
            "company_id": self.contract_id.company_id.id,
            "contract_line_id": self.id,
            "product_id": self.product_id.id,
            "date_start": period_date_start,
            "date_end": period_date_end,
            "date_invoice": recurring_next_date,
            "discount": self.discount,
            "price_unit": self.price_unit,
            "quantity": self._get_quantity_to_invoice(
                period_date_start, period_date_end, recurring_next_date
            ),
        }

    @api.multi
    def _get_contract_forecast_end_date(self):
        self.ensure_one()
        today = fields.Date.context_today(self)
        return today + self.get_relative_delta(
            self.contract_id.company_id.contract_forecast_rule_type,
            self.contract_id.company_id.contract_forecast_interval,
        )

    @api.multi
    def _get_generate_forecast_periods_criteria(self, period_date_end):
        self.ensure_one()
        if self.is_canceled or not self.active:
            return False
        contract_forecast_end_date = self._get_contract_forecast_end_date()
        if not self.date_end or self.is_auto_renew:
            return period_date_end < contract_forecast_end_date
        return (
            period_date_end < self.date_end
            and period_date_end < contract_forecast_end_date
        )

    @api.multi
    @job(default_channel=QUEUE_CHANNEL)
    def _generate_forecast_periods(self):
        values = []
        for rec in self:
            rec.forecast_period_ids.unlink()
            if rec.recurring_next_date:
                period_date_end = (
                    rec.last_date_invoiced
                    if rec.last_date_invoiced
                    else rec.date_start - relativedelta(days=1)
                )
                max_date_end = rec.date_end if not rec.is_auto_renew else False
                while (
                    period_date_end
                    and rec._get_generate_forecast_periods_criteria(
                        period_date_end
                    )
                ):
                    period_date_start = period_date_end + relativedelta(days=1)
                    period_date_end = self.get_next_period_date_end(
                        period_date_start,
                        rec.recurring_rule_type,
                        rec.recurring_interval,
                        max_date_end=max_date_end,
                    )
                    recurring_next_date = rec.get_next_invoice_date(
                        period_date_start,
                        rec.recurring_invoicing_type,
                        rec.recurring_invoicing_offset,
                        rec.recurring_rule_type,
                        rec.recurring_interval,
                        max_date_end=max_date_end,
                    )
                    if period_date_end and recurring_next_date:
                        values.append(
                            rec._prepare_contract_line_forecast_period(
                                period_date_start,
                                period_date_end,
                                recurring_next_date,
                            )
                        )

        return self.env["contract.line.forecast.period"].create(values)

    @api.model
    def create(self, values):
        contract_lines = super(ContractLine, self).create(values)
        for contract_line in contract_lines:
            contract_line.with_delay()._generate_forecast_periods()
        return contract_lines

    @api.model
    def _get_forecast_update_trigger_fields(self):
        return [
            "name",
            "sequence",
            "product_id",
            "date_start",
            "date_end",
            "quantity",
            "price_unit",
            "discount",
            "recurring_invoicing_type",
            "recurring_next_date",
            "recurring_rule_type",
            "recurring_interval",
            "is_canceled",
            "active",
            "is_auto_renew",
        ]

    @api.multi
    def write(self, values):
        res = super(ContractLine, self).write(values)
        if any(
            [
                field in values
                for field in self._get_forecast_update_trigger_fields()
            ]
        ):
            for rec in self:
                rec.with_delay()._generate_forecast_periods()
        return res
