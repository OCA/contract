# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    agreement_id = fields.Many2one("agreement", string="Agreement")
    serviceprofile_ids = fields.One2many(
        "agreement.serviceprofile", "equipment_id", string="Service Profiles"
    )
