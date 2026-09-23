# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, api, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "account.move.group.mixin"]

    @api.model
    def _get_invoice_grouping_dict(self):
        self.ensure_one()
        return {
            "partner_invoice_id": self.partner_invoice_id.id,
            "payment_term_id": self.payment_term_id.id,
            "user_id": self.user_id.id,
            "fiscal_position_id": self.fiscal_position_id.id,
            "journal_id": self.journal_id.id,
        }

    @api.model
    def _get_group_invoice_domain(self, date_ref):
        return [("invoice_status", "=", "to invoice")]

    def _prepare_group_invoices_values(self, date_ref):
        invoices_values = []
        for order in self:
            invoice_vals = order._prepare_invoice()

            if not (order_lines := order._get_invoiceable_lines()):
                continue

            invoice_line_vals = []
            for line in order_lines:
                if invoice_line_vals := line._prepare_invoice_line():
                    invoice_vals["invoice_line_ids"] += [
                        Command.create(invoice_line_vals)
                    ]

            invoices_values += [invoice_vals]
        return invoices_values
