# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    forecast_period_ids = fields.One2many(
        comodel_name="contract.line.forecast.period",
        inverse_name="contract_line_id",
        string="Forecast Periods",
        required=False,
    )

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

    def _get_contract_forecast_end_date(self):
        self.ensure_one()
        today = fields.Date.context_today(self)
        return today + self.get_relative_delta(
            self.contract_id.company_id.contract_forecast_rule_type,
            self.contract_id.company_id.contract_forecast_interval,
        )

    def _get_generate_forecast_periods_criteria(self, period_date_end):
        self.ensure_one()
        if not self.contract_id.company_id.enable_contract_forecast:
            return False
        if self.is_canceled or not self.active:
            return False
        contract_forecast_end_date = self._get_contract_forecast_end_date()
        if not self.date_end or self.is_auto_renew:
            return period_date_end < contract_forecast_end_date
        return (
            period_date_end <= self.date_end
            and period_date_end <= contract_forecast_end_date
        )

    def _generate_forecast_periods(self):
        values = []
        for rec in self:
            rec.forecast_period_ids.unlink()
            if rec.recurring_next_date:
                period_date_start = rec.next_period_date_start
                period_date_end = rec.next_period_date_end
                recurring_next_date = rec.recurring_next_date
                max_date_end = rec.date_end if not rec.is_auto_renew else False
                while period_date_end and rec._get_generate_forecast_periods_criteria(
                    period_date_end
                ):
                    if period_date_end and recurring_next_date:
                        new_vals = rec._prepare_contract_line_forecast_period(
                            period_date_start,
                            period_date_end,
                            recurring_next_date,
                        )
                        values.append(new_vals)
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

        return self.env["contract.line.forecast.period"].create(values)

    @api.model_create_multi
    def create(self, vals_list):
        contract_lines = super().create(vals_list)
        for contract_line in contract_lines:
            if contract_line.contract_id.company_id.enable_contract_forecast:
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
            "last_date_invoiced",
        ]

    def write(self, values):
        res = super().write(values)
        if any(
            [field in values for field in self._get_forecast_update_trigger_fields()]
        ):
            for rec in self:
                if rec.contract_id.company_id.enable_contract_forecast:
                    rec.with_delay()._generate_forecast_periods()
        return res
