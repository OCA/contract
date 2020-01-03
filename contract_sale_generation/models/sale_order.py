# Copyright 2019 Sylvain Van Hoof <sylvain@okia.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_id = fields.Many2one(
        'contract.contract',
        string='Contract',
        readonly=True
    )
    
    
    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()
        res = super(SaleOrder, self)._prepare_invoice()
        if self.contract_id:
            res.update({'journal_id': self.contract_id.journal_id.id})
        return res
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if res:
            if self.contract_line_id:
                res.update({'contract_line_id' : self.contract_line_id.id})
        return res
        

