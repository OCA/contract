# Copyright 2019 Sylvain Van Hoof <sylvain@okia.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_id = fields.Many2one(
        'account.analytic.account',
        string='Contract',
        readonly=True
    )
