# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):

    _inherit = "contract.contract"

    partner_delivery_zone_id = fields.Many2one(
        comodel_name="partner.delivery.zone",
        index=True,
        help="This is the partner delivery zone. If you modify this here, it"
        "will be modified on partner too.",
    )

    @api.onchange("partner_id")
    def _onchange_partner_id_contract_delivery_zone(self):
        for contract in self:
            if (
                not contract.partner_delivery_zone_id
                and contract.partner_id.delivery_zone_id
            ):
                contract.partner_delivery_zone_id = contract.partner_id.delivery_zone_id
