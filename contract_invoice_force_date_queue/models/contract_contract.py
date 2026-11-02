# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    @api.model
    def _job_prepare_context_before_enqueue_keys(self):
        """
        Keys to keep in context of stored jobs
        """
        return (
            *super()._job_prepare_context_before_enqueue_keys(),
            "invoice_date_forced",
        )

    def _recurring_create_invoice(self, date_ref=False):
        moves = super()._recurring_create_invoice(date_ref=date_ref)
        if invoice_date := self.env.context.get("invoice_date_forced", False):
            moves.write({"invoice_date": invoice_date})
        return moves
