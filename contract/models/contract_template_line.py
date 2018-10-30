# Copyright 2004-2010 OpenERP SA
# Copyright 2014 Angel Moya <angel.moya@domatix.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016-2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticContractLine(models.Model):
    _name = 'account.analytic.contract.line'
    _inherit = 'account.abstract.analytic.contract.line'
    _description = 'Contract Lines'
    _order = "sequence,id"

    contract_id = fields.Many2one(
        string='Contract',
        comodel_name='account.analytic.contract',
        required=True,
        ondelete='cascade',
        oldname='analytic_account_id',
    )
