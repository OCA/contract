# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import Command, fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        string="Analytic Tags",
        check_company=True,
    )

    def _prepare_invoice_line(self):
        vals = super()._prepare_invoice_line()
        if self.analytic_tag_ids:
            vals["analytic_tag_ids"] = [Command.set(self.analytic_tag_ids.ids)]
        return vals
