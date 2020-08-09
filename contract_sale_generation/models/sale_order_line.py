# Copyright 2019 Sylvain Van Hoof <sylvain@okia.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.addons.sale.models.sale import SaleOrderLine as OrderLine


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
        

    def _compute_invoice_status(self):
        res = super(SaleOrderLine, self)._compute_invoice_status()
        for line in self.filtered('contract_id'):
            if line.contract_template_id.type == 'invoice':
                line.invoice_status = 'no'
        return res
    
    
    @api.depends(
        'qty_invoiced',
        'qty_delivered',
        'product_uom_qty',
        'order_id.state',
        'product_id.is_contract',
        'contract_template_id',
    )
    def _get_to_invoice_qty(self):
        """
        sale line linked to contracts must not be invoiced from sale order
        """
#         res = super()._get_to_invoice_qty() #problem here, this part is setting a bad value on invoice quantity
        #maybe try to adress more precisely the super method
        for line in self:
            if line.order_id.state in ['sale', 'done']:
                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

        self.filtered('product_id.is_contract').filtered(
            lambda sol: sol.contract_template_id.type == 'invoice').update({'qty_to_invoice': 0.0})

        

