# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.translate import html_translate


class AccountAnalyticContractTemplate(models.Model):

    _name = 'account.analytic.contract.template'
    _description = 'Contract Website Templates'

    name = fields.Char(
        help='Template name',
    )
    website_description = fields.Html(
        string='Description',
        translate=html_translate,
        sanitize_attributes=False,
    )
    analytic_account_id = fields.One2many(
        string='Analytic Account',
        comodel_name='account.analytic.account',
        inverse_name='website_template_id',
    )
    analytic_contract_id = fields.One2many(
        string='Contract Template',
        comodel_name='account.analytic.account',
        inverse_name='website_template_id',
    )

    @api.multi
    def open_template(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': '/contract/template/%d' % self.id
        }
