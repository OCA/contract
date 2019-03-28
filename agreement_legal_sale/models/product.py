# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_serviceprofile = fields.Boolean(
        string="Create a Service Profile",
        help="""If True, this product will create a service profile on the
         agreement when the sales order is confirmed.""")
