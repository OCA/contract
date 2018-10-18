# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


# Main Agreement Section Records Model
class AgreementStage(models.Model):
    _name = 'agreement.stage'
    _order = 'sequence'

    # General
    name = fields.Char(
        string="Stage Name",
        required=True
    )
    description = fields.Text(
        string="Description",
        required=False
    )
    sequence = fields.Integer(
        string="Sequence",
        default="1",
        required=False
    )
    fold = fields.Boolean(
        string="Is Folded",
        required=False,
        help="This stage is folded in the kanban view by deafault."
    )
