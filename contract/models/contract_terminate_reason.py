# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractTerminateReason(models.Model):

    _name = 'contract.terminate.reason'
    _description = 'Contract Termination Reason'

    name = fields.Char(required=True)
    terminate_comment_required = fields.Boolean(
        string="Require a termination comment", default=True
    )
