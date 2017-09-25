# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticContractLine(models.Model):

    _name = 'account.analytic.contract.line'
    _description = 'Contract Lines'
    _inherit = 'account.analytic.invoice.line'

    analytic_account_id = fields.Many2one(
        string='Contract',
        comodel_name='account.analytic.contract',
        required=True,
        ondelete='cascade',
    )
