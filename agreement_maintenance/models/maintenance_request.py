# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    agreement_id = fields.Many2one("agreement", "Agreement")
    serviceprofile_id = fields.Many2one("agreement.serviceprofile", "Service Profile")
