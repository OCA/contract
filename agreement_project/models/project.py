# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    agreement_id = fields.Many2one('agreement', 'Agreement')


class ProjectTask(models.Model):
    _inherit = "project.task"

    agreement_id = fields.Many2one('agreement',
                                   related="project_id.agreement_id",
                                   string='Agreement',
                                   store=True)
