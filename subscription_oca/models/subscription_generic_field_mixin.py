# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class SubscriptionGenericFieldMixin(models.AbstractModel):
    """Generic mixin for reusable fields and duplication behavior."""

    _name = "subscription.generic.field.mixin"
    _description = "Generic mixin for subscription-related models"
    _order = "sequence, name"
    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10, index=True)

    def copy(self, default=None):
        """Add '(copy)' suffix when duplicating a record."""
        default = dict(default or {})
        if "name" not in default and self.name:
            default["name"] = _("%s (copy)", self.name)
        return super().copy(default)
