# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleSubscriptionStage(models.Model):
    _name = "sale.subscription.stage"
    _description = "Subscription stage"
    _order = "sequence, name, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer()
    in_progress = fields.Boolean(string="In progress", default=False)
    fold = fields.Boolean(string="Kanban folded")
    description = fields.Text(translate=True)
    type = fields.Selection(
        [
            ("draft", "Draft"),
            ("pre", "Ready to start"),
            ("in_progress", "In progress"),
            ("post", "Closed"),
        ],
        default="pre",
    )

    @api.constrains("type")
    def _check_lot_product(self):
        post_stages = self.env["sale.subscription.stage"].search(
            [("type", "=", "post")]
        )
        if len(post_stages) > 1:
            raise ValidationError(
                self.env._("There is already a Closed-type stage declared")
            )
