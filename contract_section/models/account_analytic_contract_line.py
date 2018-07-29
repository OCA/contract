# Copyright 2018 Road-Support - Roel Adriaans
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticContractLine(models.Model):
    _inherit = 'account.analytic.contract.line'

    layout_category_id = fields.Many2one('sale.layout_category',
                                         string='Section')
