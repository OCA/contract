# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    payment_token_id = fields.Many2one(
        string='Payment Token',
        comodel_name='payment.token',
        domain="[('id', 'in', payment_token_ids)]",
        help='This is the payment token that will be used to automatically '
             'reconcile debts for this partner, if there is not one already '
             'set on the analytic account.',
    )
