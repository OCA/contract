# Copyright 2023 Akretion - Florian Mounier
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractLinePriceHistory(models.Model):
    _inherit = "contract.line.price.history"

    type = fields.Selection(
        selection_add=[
            ("increase", "Increase"),
        ],
        ondelete={"increase": "set default"},
    )
