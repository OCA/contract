# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta


class ContractContract(models.Model):
    _inherit = "contract.contract"

    surcharge_product_id = fields.Many2one(
        string="Product", comodel_name="product.product"
    )
    surcharge_deadline = fields.Date(string="Next Deadline")
    surcharge_percent = fields.Float(string="Percentage")

    def prepare_surcharge_invoices_values(self, amount=0.0, date=False):
        self.ensure_one()
        invoice_type = "out_invoice"
        if self.contract_type == "purchase":
            invoice_type = "in_invoice"
        analytic_account_id = (
            self.contract_line_ids.mapped("analytic_account_id") or False
        )
        invoices_values = []
        # Invoice
        invoice_values = {
            "name": self.code,
            "company_id": self.company_id.id,
            "type": invoice_type,
            "partner_id": self.invoice_partner_id.id,
            "journal_id": self.journal_id.id,
            "date_invoice": fields.Date.context_today(self),
            "currency_id": self.currency_id.id,
            "origin": self.name + _(" (Surcharge)"),
            "payment_term_id": self.payment_term_id.id,
            "fiscal_position_id": self.fiscal_position_id.id,
            "user_id": self.user_id.id,
            "invoice_line_ids": [],
        }
        invoice = (
            self.env["account.invoice"]
            .with_context(
                force_company=self.company_id.id,
            )
            .new(invoice_values)
        )
        # Invoice line
        invoice_line_values = {
            "product_id": self.surcharge_product_id.id,
            "quantity": 1.0,
            "invoice_id": invoice,
        }
        invoice_line = (
            self.env["account.invoice.line"]
            .with_context(
                force_company=self.company_id.id,
            )
            .new(invoice_line_values)
        )
        invoice_line._onchange_product_id()
        invoice_line_vals = invoice_line._convert_to_write(invoice_line._cache)
        invoice_line_vals.update(
            {
                "name": _("Surcharge of the invoice of ")
                + date.strftime(DEFAULT_SERVER_DATE_FORMAT),
                "account_analytic_id": analytic_account_id
                and analytic_account_id[0].id
                or False,
                "price_unit": self.surcharge_percent * amount / 100,
            }
        )
        # Append line values to invoice values
        invoice_values["invoice_line_ids"].append((0, 0, invoice_line_vals))
        invoices_values.append(invoice_values)
        return invoices_values

    @api.model
    def cron_recurring_create_invoice(self, date_ref=None):
        res = super().cron_recurring_create_invoice(date_ref)
        # Get the contracts to surcharge
        today = fields.Date.context_today(self).strftime(DEFAULT_SERVER_DATE_FORMAT)
        contracts = self.search([("surcharge_deadline", "<=", today)])
        for contract in contracts:
            # Check that the bank statement including the surcharge deadline is
            # validated
            statement_line = self.env["account.bank.statement.line"].search(
                [("date", "=", contract.surcharge_deadline)], limit=1, order="id desc"
            )
            if (not statement_line) or (
                statement_line and statement_line.statement_id.state == "open"
            ):
                continue
            # Get the last invoice of the contract
            invoice = (
                self.env["account.invoice.line"]
                .search(
                    [("contract_line_id", "in", contract.contract_line_ids.ids)],
                    limit=1,
                    order="id desc",
                )
                .invoice_id
            )
            if invoice:
                if contract.surcharge_deadline < invoice.date_invoice:
                    contract.surcharge_deadline = (
                        contract.surcharge_deadline + relativedelta(months=1)
                    )
                # If still open, create the surcharge invoice
                if invoice.state == "open":
                    invoices_values = contract.prepare_surcharge_invoices_values(
                        invoice.amount_total, invoice.date_invoice
                    )
                    contract._finalize_and_create_invoices(invoices_values)
                    contract.surcharge_deadline = (
                        contract.surcharge_deadline + relativedelta(months=1)
                    )
                # If paid, check the payment date
                if invoice.state == "paid":
                    # Check the payment date
                    amlines = invoice.payment_move_line_ids.filtered(
                        lambda x: x.move_id.state in ["posted", "reconciled"]
                    )
                    last_payment = max([x.date for x in amlines])
                    # If paid too late, create the surcharge invoice
                    if last_payment > contract.surcharge_deadline:
                        invoices_values = contract.prepare_surcharge_invoices_values(
                            invoice.amount_total,
                            invoice.date_invoice,
                        )
                        contract._finalize_and_create_invoices(invoices_values)
                        contract.surcharge_deadline = (
                            contract.surcharge_deadline + relativedelta(months=1)
                        )
        return res
