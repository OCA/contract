# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleSubscriptionStage(models.Model):
    _name = "sale.subscription.stage"
    _description = "Subscription stage"
    _order = "sequence, name, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer()
    display_name = fields.Char(string="Display name")
    in_progress = fields.Boolean(string="In progress", default=False)
    fold = fields.Boolean(string="Kanban folded")
    description = fields.Text(translate=True)
    type = fields.Selection(
        [
            ("pre", "Ready to start"),
            ("in_progress", "In progress"),
            ("expiring", "Expiring"),
            ("post", "Closed"),
        ],
        default="pre",
    )
    is_default = fields.Boolean("Is Default", default=False)

    @api.constrains("type")
    def _check_type(self):
        post_stages = self.env["sale.subscription.stage"].search(
            [("type", "=", "post")]
        )
        if len(post_stages) > 1:
            raise ValidationError(_("There is already a Closed-type stage declared"))

    @api.constrains("is_default")
    def _check_is_default(self):
        stage_type = self.type
        default_stages = self.env["sale.subscription.stage"].search(
            [
                ("type", "=", stage_type),
                ("is_default", "=", True),
            ]
        )
        if len(default_stages) > 1:
            raise ValidationError(
                _("Can't have more than one default stage with the same type")
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "display_name" not in vals.keys():
                vals["display_name"] = vals["name"]
        res = super().create(vals_list)
        return res
