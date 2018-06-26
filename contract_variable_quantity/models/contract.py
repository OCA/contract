# Copyright 2016 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models, exceptions
from odoo.tools import float_is_zero
from odoo.tools.safe_eval import safe_eval


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    skip_zero_qty = fields.Boolean(
        string='Skip Zero Qty Lines',
        help="If checked, contract lines with 0 qty don't create invoice line",
    )

    @api.model
    def _prepare_invoice_line(self, line, invoice_id):
        vals = super(AccountAnalyticAccount, self)._prepare_invoice_line(
            line, invoice_id)
        if line.qty_type == 'variable':
            eval_context = {
                'env': self.env,
                'context': self.env.context,
                'user': self.env.user,
                'line': line,
                'contract': line.analytic_account_id,
                'invoice': self.env['account.invoice'].browse(invoice_id),
            }
            safe_eval(line.qty_formula_id.code.strip(), eval_context,
                      mode="exec", nocopy=True)  # nocopy for returning result
            qty = eval_context.get('result', 0)
            if self.skip_zero_qty and float_is_zero(
                    qty, self.env['decimal.precision'].precision_get(
                    'Product Unit of Measure')):
                # Return empty dict to skip line create
                vals = {}
            else:
                vals['quantity'] = qty
                # Re-evaluate price with this new quantity
                vals['price_unit'] = line.with_context(
                    contract_line_qty=qty,
                ).price_unit
        return vals


class AccountAnalyticContractLine(models.Model):
    _inherit = 'account.analytic.contract.line'

    qty_type = fields.Selection(
        selection=[
            ('fixed', 'Fixed quantity'),
            ('variable', 'Variable quantity'),
        ], required=True, default='fixed', string="Qty. type")
    qty_formula_id = fields.Many2one(
        comodel_name="contract.line.qty.formula", string="Qty. formula")


class ContractLineFormula(models.Model):
    _name = 'contract.line.qty.formula'

    name = fields.Char(required=True, translate=True)
    code = fields.Text(required=True, default="result = 0")

    @api.constrains('code')
    def _check_code(self):
        eval_context = {
            'env': self.env,
            'context': self.env.context,
            'user': self.env.user,
            'line': self.env['account.analytic.invoice.line'],
            'contract': self.env['account.analytic.account'],
            'invoice': self.env['account.invoice'],
        }
        try:
            safe_eval(
                self.code.strip(), eval_context, mode="exec", nocopy=True)
        except Exception as e:
            raise exceptions.ValidationError(
                _('Error evaluating code.\nDetails: %s') % e)
        if 'result' not in eval_context:
            raise exceptions.ValidationError(_('No valid result returned.'))
