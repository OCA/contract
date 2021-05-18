# Copyright 2017-2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    invoice_ids = fields.One2many(
        "account.move", "agreement_id", string="Invoices", readonly=True
    )
    out_invoice_count = fields.Integer(
        compute="_compute_invoice_count", string="# of Customer Invoices"
    )
    in_invoice_count = fields.Integer(
        compute="_compute_invoice_count", string="# of Vendor Bills"
    )

    def _compute_invoice_count(self):
        base_domain = [("agreement_id", "in", self.ids)]
        aio = self.env["account.move"]
        out_rg_res = aio.read_group(
            base_domain + [("move_type", "in", ("out_invoice", "out_refund"))],
            ["agreement_id"],
            ["agreement_id"],
        )
        out_data = {x["agreement_id"][0]: x["agreement_id_count"] for x in out_rg_res}
        in_rg_res = aio.read_group(
            base_domain + [("move_type", "in", ("in_invoice", "in_refund"))],
            ["agreement_id"],
            ["agreement_id"],
        )
        in_data = {x["agreement_id"][0]: x["agreement_id_count"] for x in in_rg_res}
        for agreement in self:
            agreement.out_invoice_count = out_data.get(agreement.id, 0)
            agreement.in_invoice_count = in_data.get(agreement.id, 0)
