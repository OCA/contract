# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractModification(models.Model):

    _name = 'contract.modification'
    _description = 'Contract Modification'
    _order = 'date desc'

    date = fields.Date(
        required=True,
        string='Date'
    )
    description = fields.Text(
        required=True,
        string='Description'
    )
    contract_id = fields.Many2one(
        string='Contract',
        comodel_name='contract.contract',
        required=True,
        ondelete='cascade',
        index=True
    )
    sent = fields.Boolean(
        string='Sent',
        default=False,
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.check_modification_ids_need_sent()
        return records

    def write(self, vals):
        res = super().write(vals)
        self.check_modification_ids_need_sent()
        return res

    def check_modification_ids_need_sent(self):
        records_not_sent = self.filtered(lambda x: not x.sent)
        if records_not_sent:
            records_not_sent.mapped('contract_id')._modification_mail_send()
