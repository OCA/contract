# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    @api.depends("display_type")
    def _compute_is_deferred(self):
        res = super()._compute_is_deferred()
        for rec in self.filtered("display_type"):
            rec.is_deferred = False
        return res

    def _check_recurring_next_date_recurring_invoices(self):
        return super(
            ContractLine, self.filtered(lambda line: not line.is_deferred)
        )._check_recurring_next_date_recurring_invoices()

    @api.depends("is_deferred")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        for rec in self:
            if rec.is_deferred:
                rec.display_name = f"Deferred - {rec.name}"
        return res

    @api.onchange("is_deferred")
    def _onchange_is_deferred(self):
        """
        If activating a contract line, make sure start/end dates are compatible
        """
        self.ensure_one()
        if not self.is_deferred:
            today = fields.date.today()
            if not self.date_start or self.date_start < today:
                self.date_start = today
            if self.date_end and self.date_end < today:
                self.date_end = False

    def _can_be_invoiced(self, date_ref):
        return not self.is_deferred and super()._can_be_invoiced(date_ref)
