# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    invoicing_sales = fields.Boolean(
        string="Invoice Pending Sales Orders",
        help="If checked include sales with same analytic account to invoice "
        "in contract invoice creation.",
    )
    invoicing_sales_into_contract = fields.Boolean(
        help="If checked, include the sales order lines "
        "in the contract invoice instead of creating separate invoices.",
    )

    def _recurring_create_invoice(self, date_ref=False):
        invoices = super()._recurring_create_invoice(date_ref)
        invoice_by_contract = {}
        for invoice in invoices:
            contract = invoice.invoice_line_ids.contract_line_id.contract_id
            invoice_by_contract[contract.id] = invoice
        for contract in self:
            if not contract.invoicing_sales or not contract.recurring_next_date:
                continue
            common_domain = [
                (
                    "partner_invoice_id",
                    "child_of",
                    contract.partner_id.commercial_partner_id.ids,
                ),
                ("invoice_status", "=", "to invoice"),
                (
                    "date_order",
                    "<=",
                    f"{contract.recurring_next_date} 23:59:59",
                ),
            ]
            sales = self.env["sale.order"].search(
                common_domain
                + [
                    ("analytic_account_id", "=", contract.group_id.id),
                ]
            )
            sales |= self.env["sale.order"].search(
                common_domain
                + [
                    (
                        "order_line.distribution_analytic_account_ids",
                        "in",
                        self.group_id.ids,
                    )
                ]
            )
            sales = sales.with_context(
                filter_on_analytic_account=contract.group_id.id
            ).filtered(lambda s: s._get_invoiceable_lines())
            if not sales:
                continue
            # Add sales lines to existing invoice
            if contract.invoicing_sales_into_contract and invoice_by_contract.get(
                contract.id
            ):
                invoice = invoice_by_contract[contract.id]
                sale_lines_to_invoice = sales.with_context(
                    filter_on_analytic_account=contract.group_id.id
                )._get_invoiceable_lines()
                next_sequence = (
                    max(invoice.invoice_line_ids.mapped("sequence") or [0]) + 1
                )
                invoice_line_vals_list = []
                for sale_line in sale_lines_to_invoice:
                    invoice_line_vals = sale_line._prepare_invoice_line(
                        sequence=next_sequence
                    )
                    next_sequence += 1
                    invoice_line_vals["move_id"] = invoice.id
                    invoice_line_vals_list.append(invoice_line_vals)
                self.env["account.move.line"].create(invoice_line_vals_list)
            else:
                # Create separate invoices for sales
                invoices |= sales._create_invoices()
        return invoices
