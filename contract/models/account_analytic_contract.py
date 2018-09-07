# Copyright 2004-2010 OpenERP SA
# Copyright 2014 Angel Moya <angel.moya@domatix.com>
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2015-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticContract(models.Model):
    _name = 'account.analytic.contract'

    # These fields will not be synced to the contract
    NO_SYNC = [
        'name',
        'partner_id',
    ]

    name = fields.Char(
        required=True,
    )
    # Needed for avoiding errors on several inherited behaviors
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner (always False)",
    )
    contract_type = fields.Selection(
        selection=[
            ('sale', 'Customer'),
            ('purchase', 'Supplier'),
        ], default='sale',
    )
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist',
    )
    recurring_invoice_line_ids = fields.One2many(
        comodel_name='account.analytic.contract.line',
        inverse_name='analytic_account_id',
        copy=True,
        string='Invoice Lines',
    )
    recurring_rule_type = fields.Selection(
        [('daily', 'Day(s)'),
         ('weekly', 'Week(s)'),
         ('monthly', 'Month(s)'),
         ('monthlylastday', 'Month(s) last day'),
         ('yearly', 'Year(s)'),
         ],
        default='monthly',
        string='Recurrence',
        help="Specify Interval for automatic invoice generation.",
    )
    recurring_invoicing_type = fields.Selection(
        [('pre-paid', 'Pre-paid'),
         ('post-paid', 'Post-paid'),
         ],
        default='pre-paid',
        string='Invoicing type',
        help="Specify if process date is 'from' or 'to' invoicing date",
    )
    recurring_interval = fields.Integer(
        default=1,
        string='Repeat Every',
        help="Repeat every (Days/Week/Month/Year)",
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        default=lambda s: s._default_journal(),
        domain="[('type', '=', contract_type),"
               "('company_id', '=', company_id)]",
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id,
    )

    @api.onchange('contract_type')
    def _onchange_contract_type(self):
        if self.contract_type == 'purchase':
            self.recurring_invoice_line_ids.filtered('automatic_price').update(
                {'automatic_price': False})
        self.journal_id = self.env['account.journal'].search([
            ('type', '=', self.contract_type),
            ('company_id', '=', self.company_id.id)
        ], limit=1)

    @api.model
    def _default_journal(self):
        company_id = self.env.context.get(
            'company_id', self.env.user.company_id.id)
        domain = [
            ('type', '=', self.contract_type),
            ('company_id', '=', company_id)]
        return self.env['account.journal'].search(domain, limit=1)
