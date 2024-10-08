# Copyright 2023 Domatix - Carlos Martínez
# Copyright 2024 Binhex - Adasat Torres de León
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    subscribable = fields.Boolean(string="Subscribable product")
    subscription_template_id = fields.Many2one(
        comodel_name="sale.subscription.template", string="Subscription template"
    )


class ProductProduct(models.Model):
    _inherit = "product.product"

    subscribable = fields.Boolean(string="Subscribable product")
    subscription_template_id = fields.Many2one(
        comodel_name="sale.subscription.template", string="Subscription template"
    )
