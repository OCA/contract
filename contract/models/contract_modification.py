# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractModification(models.Model):

    _name = "contract.modification"
    _description = "Contract Modification"
    _order = "date desc"

    date = fields.Date(required=True)
    description = fields.Text(required=True)
    contract_id = fields.Many2one(
        string="Contract",
        comodel_name="contract.contract",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sent = fields.Boolean(default=False)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.context.get("bypass_modification_send"):
            records.check_modification_ids_need_sent()
        return records

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get("bypass_modification_send"):
            self.check_modification_ids_need_sent()
        return res

    def check_modification_ids_need_sent(self):
        self.mapped("contract_id")._modification_mail_send()
