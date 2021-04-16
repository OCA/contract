# Copyright 2016 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools import float_is_zero
from odoo.tools.safe_eval import safe_eval


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = "contract.line"

    def _get_quantity_to_invoice(
        self, period_first_date, period_last_date, invoice_date
    ):
        quantity = super()._get_quantity_to_invoice(
            period_first_date, period_last_date, invoice_date
        )
        if not period_first_date or not period_last_date or not invoice_date:
            return quantity
        if self.qty_type == "variable":
            eval_context = {
                "env": self.env,
                "context": self.env.context,
                "user": self.env.user,
                "line": self,
                "quantity": quantity,
                "period_first_date": period_first_date,
                "period_last_date": period_last_date,
                "invoice_date": invoice_date,
                "contract": self.contract_id,
            }
            safe_eval(
                self.qty_formula_id.code.strip(),
                eval_context,
                mode="exec",
                nocopy=True,
            )  # nocopy for returning result
            quantity = eval_context.get("result", 0)
        return quantity

    def _prepare_invoice_line(self, move_form):
        vals = super()._prepare_invoice_line(move_form)
        if (
            "quantity" in vals
            and self.contract_id.skip_zero_qty
            and float_is_zero(
                vals["quantity"],
                self.env["decimal.precision"].precision_get("Product Unit of Measure"),
            )
        ):
            vals = {}
        return vals
