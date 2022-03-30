# Copyright 2022 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import models


class ContractLine(models.Model):
    _inherit = "contract.line"

    # Exclude constraint check for contract using invoice plan
    def _check_allowed(self):
        self = self.filtered(lambda l: not l.contract_id.use_invoice_plan)
        super()._check_allowed()

    def _check_overlap_successor(self):
        self = self.filtered(lambda l: not l.contract_id.use_invoice_plan)
        super()._check_overlap_successor()

    def _check_overlap_predecessor(self):
        self = self.filtered(lambda l: not l.contract_id.use_invoice_plan)
        super()._check_overlap_predecessor()

    def _check_auto_renew_canceled_lines(self):
        self = self.filtered(lambda l: not l.contract_id.use_invoice_plan)
        super()._check_auto_renew_canceled_lines()

    def _check_recurring_next_date_start_date(self):
        self = self.filtered(lambda l: not l.contract_id.use_invoice_plan)
        super()._check_recurring_next_date_start_date()

    def _check_last_date_invoiced(self):
        self = self.filtered(lambda l: not l.contract_id.use_invoice_plan)
        super()._check_last_date_invoiced()

    def _check_recurring_next_date_recurring_invoices(self):
        self = self.filtered(lambda l: not l.contract_id.use_invoice_plan)
        super()._check_recurring_next_date_recurring_invoices()

    def _check_start_end_dates(self):
        self = self.filtered(lambda l: not l.contract_id.use_invoice_plan)
        super()._check_start_end_dates()

    def unlink(self):
        # Set cancelled for contract invoice plan, so it can be unlinked
        self_use_ip = self.filtered("contract_id.use_invoice_plan")
        self_use_ip.write({"is_canceled": True})
        return super().unlink()
