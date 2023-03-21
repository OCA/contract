# Copyright 2023 Akretion - Florian Mounier
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class ContractLine(models.Model):
    _inherit = "contract.line"

    price_history_ids = fields.One2many(
        comodel_name="contract.line.price.history",
        inverse_name="contract_line_id",
        string="Price History",
    )

    @api.model
    def create(self, vals):
        if vals.get("price_unit"):
            # At creation, we create a new price history
            # with type initial
            vals["price_history_ids"] = [
                (
                    0,
                    0,
                    {
                        "new_price": vals["price_unit"],
                        "date": fields.Date.today(),
                        "type": "initial",
                        "contract_line_id": self.id,
                    },
                )
            ]

        return super(ContractLine, self).create(vals)

    def write(self, vals):
        if (
            "price_unit" in vals
            and float_compare(self.price_unit, vals["price_unit"], precision_digits=2)
            != 0
        ):
            # If price unit is updated, we create a new price history
            # The type of the price history can be defined by the context
            self.env["contract.line.price.history"].create(
                {
                    "old_price": self.price_unit,
                    "new_price": vals["price_unit"],
                    "date": fields.Date.today(),
                    "type": self._context.get("price_unit_update_type", "update"),
                    "contract_line_id": self.id,
                }
            )

        return super(ContractLine, self).write(vals)
