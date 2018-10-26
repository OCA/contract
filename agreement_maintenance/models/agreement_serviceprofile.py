# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


PROFILE_TYPE = [
    ('equipment', 'Equipment'),
    ('product', 'Product')
]


class AgreementServiceProfile(models.Model):
    _name = 'agreement.serviceprofile'

    name = fields.Char(string="Name", required=True)
    profile_type = fields.Selection(
        PROFILE_TYPE,
        string="Profile Type")
    description = fields.Text(string="Description")
    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string="Equipment")
    product_id = fields.Many2one(
        'product.product',
        string="Product",
        domain=[('serviceprofile_ok', '=', True)])
    equipment_category_id = fields.Many2one(
        'maintenance.equipment.category',
        related='equipment_id.category_id',
        string="Equipment Category",
        readonly=1)
    agreement_id = fields.Many2one(
        'agreement',
        string="Agreement",
        ondelete="cascade",
        required=True)
    fsm_location_id = fields.Many2one(
        'fsm.location',
        string="Service Location")
