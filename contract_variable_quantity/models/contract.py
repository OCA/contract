# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models, exceptions
from odoo.tools.safe_eval import safe_eval


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

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
            vals['quantity'] = eval_context.get('result', 0)
        return vals


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    qty_type = fields.Selection(
        selection=[
            ('fixed', 'Fixed quantity'),
            ('variable', 'Variable quantity'),
        ], required=True, default='fixed', string="Qty. type")
    qty_formula_id = fields.Many2one(
        comodel_name="contract.line.qty.formula", string="Qty. formula")


class ContractLineFormula(models.Model):
    _name = 'contract.line.qty.formula'

    name = fields.Char(required=True)
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
