# Copyright 2019 ACSONE SA/NV
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_payment_mode_id = fields.Many2one(
        comodel_name='account.payment.mode',
        string='Contract Payment Mode',
        domain=[('payment_type', '=', 'inbound')],
        index=True,
    )
    specific_contract_payment_mode = fields.Boolean(
        related="company_id.specific_contract_payment_mode",
        string="Different payment mode for contracts generated from sale "
               "orders",
    )

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        if self.partner_id:
            self.contract_payment_mode_id = self.partner_id.with_context(
                force_company=self.company_id.id
            ).customer_payment_mode_id
        else:
            self.payment_mode_id = False
        return res

    @api.multi
    def _prepare_contract_value(self, contract_template):
        self.ensure_one()
        vals = super(SaleOrder, self)._prepare_contract_value(
            contract_template)
        if self.specific_contract_payment_mode:
            vals['payment_mode_id'] = self.contract_payment_mode_id.id
        else:
            vals['payment_mode_id'] = self.payment_mode_id.id
        return vals
