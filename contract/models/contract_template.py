# Copyright 2004-2010 OpenERP SA
# Copyright 2014 Angel Moya <angel.moya@domatix.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016-2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticContract(models.Model):
    _name = 'account.analytic.contract'
    _inherit = 'account.abstract.analytic.contract'
    _description = "Account Analytic Contract"

    recurring_invoice_line_ids = fields.One2many(
        comodel_name='account.analytic.contract.line',
        inverse_name='contract_id',
        copy=True,
        string='Invoice Lines',
    )
