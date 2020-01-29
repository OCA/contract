# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractResiliateReason(models.Model):

    _name = 'contract.resiliate.reason'
    _description = 'Contract Resiliation Reason'

    name = fields.Char(required=True)
