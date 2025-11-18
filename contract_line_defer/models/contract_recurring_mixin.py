# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractRecurringMixin(models.AbstractModel):
    _inherit = "contract.recurring.mixin"

    is_deferred = fields.Boolean(
        "Deferred",
        compute="_compute_is_deferred",
        store=True,
        precompute=True,
        readonly=False,
        help="Do not invoice this line until it is activated",
    )

    def _compute_is_deferred(self):
        """
        Stored and no depends: only computed at creation to set default
        """
        for rec in self:
            rec.is_deferred = rec.company_id.defer_contract_line_start

    def enable_deferred(self):
        self.ensure_one()
        self.is_deferred = True

    @api.depends("is_deferred")
    def _compute_recurring_next_date(self):
        """No next invoice date for deferred lines"""
        res = super()._compute_recurring_next_date()
        self.filtered(lambda r: r.is_deferred).update({"recurring_next_date": False})
        return res

    @api.depends("is_deferred")
    def _compute_next_period_date_start(self):
        return super()._compute_next_period_date_start()
