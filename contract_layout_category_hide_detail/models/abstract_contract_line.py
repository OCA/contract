# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ContractAbstractContractLine(models.AbstractModel):
    _inherit = 'contract.abstract.contract.line'

    show_details = fields.Boolean(
        string="Show details",
        default=True
    )
    show_subtotal = fields.Boolean(
        string="Show subtotal",
        default=True
    )
