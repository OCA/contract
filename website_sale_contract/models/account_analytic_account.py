# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    customer_signature = fields.Binary(
        string='Customer acceptance',
    )
    signature_name = fields.Char(
        string='Signed By',
    )
