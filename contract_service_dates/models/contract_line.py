# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    service_start_date = fields.Date(
        help="Start date of the service period covered by this contract line. "
        "Defaults to the contract line start date and follows it unless "
        "manually overridden.",
    )
    service_end_date = fields.Date(
        help="End date of the service period covered by this contract line. "
        "Defaults to the contract line end date and follows it unless "
        "manually overridden.",
    )

    def _get_service_date_create_vals(self, vals):
        """Return service date vals to initialize on create."""
        result = {}
        if vals.get("date_start") and not vals.get("service_start_date"):
            result["service_start_date"] = vals["date_start"]
        if vals.get("date_end") and not vals.get("service_end_date"):
            result["service_end_date"] = vals["date_end"]
        return result

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update(self._get_service_date_create_vals(vals))
        return super().create(vals_list)

    def _get_service_date_sync_vals(self, vals):
        """Return service date vals to sync from contract date vals."""
        self.ensure_one()
        service_vals = {}
        if "date_start" in vals and self.service_start_date == self.date_start:
            service_vals["service_start_date"] = vals["date_start"]
        if "date_end" in vals and self.service_end_date == self.date_end:
            service_vals["service_end_date"] = vals["date_end"]
        return service_vals

    def write(self, vals):
        if not self.env.context.get("_sync_service_dates"):
            service_vals_by_id = {}
            for rec in self:
                service_vals = rec._get_service_date_sync_vals(vals)
                if service_vals:
                    service_vals_by_id[rec.id] = service_vals
            for rec in self:
                if rec.id in service_vals_by_id:
                    rec.with_context(_sync_service_dates=True).write(
                        service_vals_by_id[rec.id]
                    )
        return super().write(vals)
