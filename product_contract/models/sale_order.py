# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2019 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# pylint: disable=missing-docstring,protected-access
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        """ If we have a contract in the order, set it up """
        for order in self:
            # create_contract() already filters on contract order lines.
            order.order_line.create_contract()
        return super(SaleOrder, self).action_confirm()
