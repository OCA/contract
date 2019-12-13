# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_id = fields.Many2one(
        comodel_name="contract.contract",
        string="Contract"
    )

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        invoice_ids = self.env['account.invoice'].search([
            ('partner_id', '=', self.partner_id.id),
            ('old_contract_id', '=', self.contract_id.id),
            ('state', '=', 'draft')])

        for invoice_id in invoice_ids:
            for order_line in self.order_line:
                for invoice_line in invoice_id.invoice_line_ids:
                    if order_line.product_id.id == invoice_line.product_id.id:
                        invoice_line.quantity += order_line.product_uom_qty
        self.action_invoice_create()
        return res
