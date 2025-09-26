# Copyright 2025 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractInvoicePeriodWizard(models.TransientModel):
    _name = "contract.invoice.period.wizard"
    _description = "Selecionar Período para Faturamento"

    contract_id = fields.Many2one("contract.contract", required=True, readonly=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)

    def action_confirm(self):
        self.contract_id.calculate_total_hours(self.date_start, self.date_end)
        return (
            self.contract_id.with_context(from_wizard=True)
            .sudo()
            ._recurring_create_invoice_super()
        )
