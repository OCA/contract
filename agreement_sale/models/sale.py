# Copyright 2017-2020 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    agreement_id = fields.Many2one(
        comodel_name="agreement",
        string="Agreement",
        ondelete="restrict",
        tracking=True,
        readonly=True,
        copy=False,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    )

    agreement_type_id = fields.Many2one(
        comodel_name="agreement.type",
        string="Agreement Type",
        ondelete="restrict",
        tracking=True,
        readonly=True,
        copy=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    )

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        vals["agreement_id"] = self.agreement_id.id or False
        return vals
