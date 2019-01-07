# Copyright 2016 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_is_zero
from odoo.tools.safe_eval import safe_eval


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    @api.multi
    def _prepare_invoice_line(self, invoice_id=False):
        vals = super(AccountAnalyticInvoiceLine, self)._prepare_invoice_line(
            invoice_id=invoice_id
        )
        if self.qty_type == 'variable':
            eval_context = {
                'env': self.env,
                'context': self.env.context,
                'user': self.env.user,
                'line': self,
                'contract': self.contract_id,
                'invoice': self.env['account.invoice'].browse(invoice_id),
            }
            safe_eval(
                self.qty_formula_id.code.strip(),
                eval_context,
                mode="exec",
                nocopy=True,
            )  # nocopy for returning result
            qty = eval_context.get('result', 0)
            if self.contract_id.skip_zero_qty and float_is_zero(
                qty,
                self.env['decimal.precision'].precision_get(
                    'Product Unit of Measure'
                ),
            ):
                # Return empty dict to skip line create
                vals = {}
            else:
                vals['quantity'] = qty
                # Re-evaluate price with this new quantity
                vals['price_unit'] = self.with_context(
                    contract_line_qty=qty
                ).price_unit
        else:
            if 'quantity' in vals and vals['quantity'] == 0:
                # Skip zero should ignore lines with qty zero even for fixed
                # qty
                vals = {}
        return vals
