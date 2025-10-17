# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleSubscriptionTag(models.Model):
    _name = "sale.subscription.tag"
    _inherit = ["subscription.generic.field.mixin"]
    _description = "Tags for sale subscription"
