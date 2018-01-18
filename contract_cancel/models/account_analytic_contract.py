# -*- coding: utf-8 -*-
# Copyright 2018 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAnalyticContract(models.Model):

    _inherit = 'account.analytic.contract'

    auto_cancel_contract = fields.Boolean(
        string='Auto Cancel',
        help='Enabling will cause the contract recurring '
             'invoices option to be disabled (effectively '
             'canceling the contract) when an invoice is '
             'past due.',
    )
