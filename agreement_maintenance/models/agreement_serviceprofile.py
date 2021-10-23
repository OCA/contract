# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AgreementServiceProfile(models.Model):
    _inherit = "agreement.serviceprofile"

    equipment_id = fields.Many2one("maintenance.equipment", string="Equipment")
