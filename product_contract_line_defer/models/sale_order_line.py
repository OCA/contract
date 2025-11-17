# Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_contract_line_values(self, contract, predecessor_contract_line=False):
        values = super()._prepare_contract_line_values(
            contract, predecessor_contract_line
        )
        values["is_deferred"] = self.is_deferred
        return values

    @api.depends(
        "is_deferred",
    )
    def _compute_name(self):
        res = super()._compute_name()
        for line in self:
            if line.is_contract:
                if line.is_deferred:
                    date_text = "Deferred"
                    recurring_rule_label = dict(
                        self._fields["recurrence_interval"]._description_selection(
                            self.env
                        )
                    ).get(line.recurring_rule_type)
                    invoicing_type_label = dict(
                        self._fields["recurring_invoicing_type"]._description_selection(
                            self.env
                        )
                    ).get(line.recurring_invoicing_type)
                    line.name = line._get_contract_name(
                        date_text, recurring_rule_label, invoicing_type_label
                    )
        return res
