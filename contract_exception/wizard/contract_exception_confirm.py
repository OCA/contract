# Copyright 2024 Foodles (https://www.foodles.co/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ContractExceptionConfirm(models.TransientModel):
    _name = "contract.exception.confirm"
    _description = "Contract exception wizard"
    _inherit = ["exception.rule.confirm"]

    related_model_id = fields.Many2one(
        comodel_name="contract.contract", string="Contract"
    )

    date = fields.Date(required=True)

    def action_confirm(self):
        self.ensure_one()
        if self.ignore:
            self.related_model_id.ignore_exception = True
            self.related_model_id.generate_invoices_manually(self.date)
        return super().action_confirm()
