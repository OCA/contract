# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    next_bill_method = fields.Selection(
        selection=[
            ("auto", "Next bill by sequence"),
            ("manual", "Next bill by manual selection"),
        ],
        help="Saved default method for this contract",
    )


class ContractLine(models.Model):
    _inherit = "contract.line"

    invoice_lines = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="contract_line_id",
        copy=False,
    )
    qty_to_invoice = fields.Float(
        compute="_compute_qty_to_invoice",
        string="To Invoice",
        digits="Product Unit of Measure",
        store=True,
    )

    @api.depends("invoice_lines.move_id.state", "invoice_lines.quantity", "quantity")
    def _compute_qty_to_invoice(self):
        for line in self:
            # compute qty_invoiced
            qty_invoiced = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.move_id.state not in ["cancel"]:
                    if inv_line.move_id.move_type in [
                        "in_invoice",
                        "out_invoice",
                    ]:
                        qty_invoiced += inv_line.product_uom_id._compute_quantity(
                            inv_line.quantity, line.uom_id
                        )
                    elif inv_line.move_id.move_type in [
                        "in_refund",
                        "out_refund",
                    ]:
                        qty_invoiced -= inv_line.product_uom_id._compute_quantity(
                            inv_line.quantity, line.uom_id
                        )
            # compute qty_to_invoice
            line.qty_to_invoice = line.quantity - qty_invoiced

    def _prepare_invoice_line(self, move_form):
        self.ensure_one()
        invoice_qty_line_ids = self._context.get("invoice_qty_line_ids", [])
        if not invoice_qty_line_ids or any(
            line["contract_line_id"] == self.id for line in invoice_qty_line_ids
        ):
            return super()._prepare_invoice_line(move_form)
        return {}


class ContractInvoicePlan(models.Model):
    _inherit = "contract.invoice.plan"

    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (
                    rec.id,
                    "%s %s : %s -- %s%s -- %s"
                    % (
                        _("Installment"),
                        rec.installment,
                        rec.plan_date,
                        round(rec.percent, 2),
                        "%",
                        "{:,.2f}".format(rec.amount),
                    ),
                )
            )
        return result

    def _get_plan_qty(self, contract_line, percent):
        """If manual select installment, use it for qty"""
        plan_qty = super()._get_plan_qty(contract_line, percent)
        if self.env.context.get("next_bill_method") == "manual":
            res = list(
                filter(
                    lambda l: l["contract_line_id"] == contract_line.id,
                    self.env.context["invoice_qty_line_ids"],
                )
            )
            if res:
                plan_qty = res[0].get("quantity")
            else:
                plan_qty = 0
        return plan_qty
