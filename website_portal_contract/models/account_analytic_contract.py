# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountAnalyticContract(models.Model):

    _inherit = 'account.analytic.contract'

    website_template_id = fields.Many2one(
        string='Website Template',
        comodel_name='account.analytic.contract.template',
        help='Website layout for contract',
        default=lambda s: s._get_default_template(),
    )

    @api.model
    def _get_default_template(self):
        return self.env.ref(
            'website_portal_contract.website_contract_template_default',
            raise_if_not_found=False,
        )
