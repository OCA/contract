# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contract_invoice_merge = fields.Boolean()
