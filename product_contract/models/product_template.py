# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_contract = fields.Boolean('Is a contract')
    contract_template_id = fields.Many2one(
        comodel_name='account.analytic.contract', string='Contract Template'
    )

    @api.onchange('is_contract')
    def _change_is_contract(self):
        """ Clear the relation to contract_template_id when downgrading
        product from contract
        """
        if not self.is_contract:
            self.contract_template_id = False

    @api.constrains('is_contract', 'type')
    def _check_contract_product_type(self):
        """
        Contract product should be service type
        """
        if self.is_contract and self.type != 'service':
            raise ValidationError(_("Contract product should be service type"))
