# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractAbstractContract(models.Model):
    _inherit = "contract.template"

    transmit_method_id = fields.Many2one(
        comodel_name="transmit.method",
        string="Transmission Method",
        ondelete="restrict",
        compute="_compute_transmit_method_id",
        readonly=False,
        store=True,
    )

    @api.depends("partner_id", "company_id")
    def _compute_transmit_method_id(self):
        for rec in self:
            transmit_method = False
            if rec.partner_id and rec.contract_type:
                if rec.contract_type == "sale":
                    transmit_method = rec.partner_id.customer_invoice_transmit_method_id
                else:
                    transmit_method = rec.partner_id.supplier_invoice_transmit_method_id
            rec.transmit_method_id = transmit_method
