# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models, exceptions
from odoo.tools.safe_eval import safe_eval


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    @api.multi
    def _convert_contract_lines(self, contract):
        res = super(AccountAnalyticAccount, self).\
            _convert_contract_lines(contract)
        for item in res:
            vals = item[2]
            line = self.partner_id
            if vals['discount_type'] == 'variable':
                eval_context = {
                    'env': self.env,
                    'context': self.env.context,
                    'user': self.env.user,
                    'partner': self.partner_id,
                    'line': line,
                    'contract': self
                }
                discount_formula_id = self.env[
                    'contract.line.discount.formula'].browse(
                    vals['discount_formula_id'])
                safe_eval(discount_formula_id.code.strip(), eval_context,
                          mode="exec",
                          nocopy=True)  # nocopy for returning result
                vals['discount'] = eval_context.get('result', 0)
        return res


class AccountAnalyticContractLine(models.Model):
    _inherit = 'account.analytic.contract.line'

    discount_type = fields.Selection(
        selection=[
            ('fixed', 'Fixed discount'),
            ('variable', 'Variable discount'),
        ], required=True, default='fixed', string="Discount type")
    discount_formula_id = fields.Many2one(
        comodel_name="contract.line.discount.formula", string="Formula")


class ContractLineFormula(models.Model):
    _name = 'contract.line.discount.formula'

    name = fields.Char(required=True)
    code = fields.Text(required=True, default="result = 0")

    @api.constrains('code')
    def _check_code(self):
        eval_context = {
            'env': self.env,
            'context': self.env.context,
            'user': self.env.user,
            'partner': self.env.user.partner_id,
            'line': self.env['account.analytic.invoice.line'],
            'contract': self.env['account.analytic.account'],
        }
        try:
            safe_eval(
                self.code.strip(), eval_context, mode="exec", nocopy=True)
        except Exception as e:
            raise exceptions.ValidationError(
                _('Error evaluating code.\nDetails: %s') % e)
        if 'result' not in eval_context:
            raise exceptions.ValidationError(_('No valid result returned.'))
