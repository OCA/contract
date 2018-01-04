# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    contract_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Contract'
    )
