# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from odoo.addons import decimal_precision as dp


class AccountAnalyticInvoiceLine(models.Model):
    _name = 'account.analytic.invoice.line'
    _inherit = 'account.analytic.contract.line'

    @api.depends('invoice_lines.invoice_id.state',
                 'invoice_lines.quantity',
                 'invoice_lines.uom_id')
    def _compute_qty_invoiced(self):
        for line in self:
            qty = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.invoice_id.state not in ['cancel']:
                    if inv_line.invoice_id.type in [
                        'in_invoice', 'out_invoice'
                    ]:
                        qty += inv_line.uom_id._compute_quantity(
                            inv_line.quantity, line.uom_id)
                    elif inv_line.invoice_id.type in [
                        'out_refund', 'in_refund'
                    ]:
                        qty -= inv_line.uom_id._compute_quantity(
                            inv_line.quantity, line.uom_id)
            line.qty_invoiced = qty

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        required=True,
        ondelete='cascade',
    )
    qty_invoiced = fields.Float(
        compute='_compute_qty_invoiced',
        string='Invoiced Qty',
        store=True,
        digits=dp.get_precision('Product Unit of Measure')
    )
    invoice_lines = fields.One2many(
        comodel_name='account.invoice.line',
        inverse_name='contract_line_id',
        string="Invoiced Lines",
        readonly=True,
        copy=False
    )
