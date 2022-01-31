# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractContract(models.Model):

    _inherit = "contract.contract"

    picking_note = fields.Text(string="Picking Internal Note")
    picking_customer_note = fields.Text(string="Picking Customer Comments")

    def _prepare_sale(self, date_ref):
        res = super()._prepare_sale(date_ref)
        res.update(
            {
                "picking_note": self.picking_note,
                "picking_customer_note": self.picking_customer_note,
            }
        )
        return res
