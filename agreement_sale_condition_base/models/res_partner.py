# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    default_agreement_type_id = fields.Many2one(
        comodel_name='agreement.type',
        string='Default Agreement Type'
    )
    customer_agreement_settings_id = fields.Many2one(
        comodel_name='agreement',
        domain=[('is_customer_requirement', '=', True)],
        string="Agreed customer preferences"
    )
    customer_agreements = fields.One2many(
        comodel_name='agreement', inverse_name='partner_id',
        string="All agreements"
    )
