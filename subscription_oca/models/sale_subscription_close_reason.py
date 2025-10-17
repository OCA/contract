# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleSubscriptionCloseReason(models.Model):
    _name = "sale.subscription.close.reason"
    _inherit = ["subscription.generic.field.mixin"]
    _description = "Close reason model"
    _order = "sequence, name, id"
