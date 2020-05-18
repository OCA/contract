# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractAbstractContract(models.AbstractModel):

    _inherit = "contract.abstract.contract"

    transmit_method_id = fields.Many2one(
        comodel_name="transmit.method",
        string="Transmission Method",
        track_visibility="onchange",
        ondelete="restrict",
    )

    @api.onchange("partner_id", "company_id")
    def onchange_partner_transmit_method(self):
        if self.partner_id and self.contract_type:
            if self.contract_type == "sale":
                self.transmit_method_id = (
                    self.partner_id.customer_invoice_transmit_method_id.id
                    or False
                )
            else:
                self.transmit_method_id = (
                    self.partner_id.supplier_invoice_transmit_method_id.id
                    or False
                )
