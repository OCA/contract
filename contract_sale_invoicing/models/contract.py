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

    def _recurring_create_invoice(self, date_ref=False):
        invoices = super()._recurring_create_invoice(date_ref)
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
            if sales:
                invoices |= sales._create_invoices()
        return invoices
