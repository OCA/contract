# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


# Main Stage on the Agreement
class AgreementStage(models.Model):
    _name = "agreement.stage"
    _description = "Agreement Stages"
    _order = "sequence"

    # General
    name = fields.Char(string="Stage Name", required=True)
    sequence = fields.Integer(string="Sequence", default="1", required=False)
    fold = fields.Boolean(
        string="Is Folded",
        required=False,
        help="This stage is folded in the kanban view by default.",
    )
    stage_type = fields.Selection(
        [("agreement", "Agreement")], string="Type", required=True
    )
    active = fields.Boolean(string="Active", default=True)
    readonly = fields.Boolean(
        string="Readonly",
        default=False,
        help="The agreement can not edit if set Readonly = True.",
    )
