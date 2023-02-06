# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class ContractMakePlannedInvoice(models.TransientModel):
    _name = "contract.make.planned.invoice"
    _description = "Wizard when create invoice by plan"

    def create_invoices_by_plan(self):
        contract = self.env["contract.contract"].browse(self._context.get("active_id"))
        contract.ensure_one()
        invoice_plans = (
            self._context.get("all_remain_invoices")
            and contract.invoice_plan_ids.filtered(lambda l: not l.invoiced)
            or contract.invoice_plan_ids.filtered("to_invoice")
        )
        for plan in invoice_plans.sorted("installment"):
            contract.sudo().with_context(
                invoice_plan_id=plan.id
            ).action_ip_create_invoice()
        return {"type": "ir.actions.act_window_close"}
