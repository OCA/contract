# Copyright 2019 Sylvain Van Hoof <sylvain@okia.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    created_from_contract_line_id = fields.Many2one(
        comodel_name="contract.line",
        string="Created from Contract Line ",
        required=False,
        copy=False,
    )

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if res:
            if self.created_from_contract_line_id:
                res.update({'contract_line_id' : self.created_from_contract_line_id.id})
        return res
        

