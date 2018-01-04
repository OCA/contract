# -*- coding: utf-8 -*-
# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticContract(models.Model):
    _inherit = 'account.analytic.contract'

    type = fields.Selection(
        string='Type',
        selection=[('invoice', 'Invoice'),
                   ('sale', 'Sale')],
        default='invoice',
        required=True,
    )
    sale_autoconfirm = fields.Boolean(
        string='Sale autoconfirm')
