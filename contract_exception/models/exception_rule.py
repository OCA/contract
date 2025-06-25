# Copyright 2024 Foodles (https://www.foodles.co/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ExceptionRule(models.Model):
    _inherit = "exception.rule"

    contract_ids = fields.Many2many(
        comodel_name="contract.contract", string="Contracts"
    )
    model = fields.Selection(
        selection_add=[
            ("contract.contract", "Contract"),
            ("contract.line", "Contract line"),
        ],
        ondelete={
            "contract.contract": "cascade",
            "contract.line": "cascade",
        },
    )
