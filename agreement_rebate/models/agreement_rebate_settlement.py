# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, models, fields
from odoo.osv import expression
from odoo.tools import safe_eval
from odoo.exceptions import UserError


class AgreementRebateSettlement(models.Model):
    _name = 'agreement.rebate.settlement'
    _description = 'Agreement Rebate Settlement'

    name = fields.Char()
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        related='agreement_id.company_id',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('invoiced', 'Invoiced'),
        ],
        compute='_compute_state',
        string='State',
        store=True,
    )
    date = fields.Date(default=fields.Date.today())
    date_from = fields.Date()
    date_to = fields.Date()
    agreement_id = fields.Many2one(
        comodel_name='agreement',
        string='Agreement',
        required=True,
    )
    rebate_type = fields.Selection(
        related='agreement_id.rebate_type',
        string='Rebate type',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        related='agreement_id.partner_id',
        store=True,
    )
    line_ids = fields.One2many(
        comodel_name='agreement.rebate.settlement.line',
        inverse_name='rebate_settlement_id',
        string='Settlement Lines',
    )
    amount_invoiced = fields.Float(string='Amount invoiced')
    amount_rebate = fields.Float(string='Amount rebate')
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice'
    )

    @api.depends('invoice_id')
    def _compute_state(self):
        for rec in self:
            rec.state = rec.invoice_id and 'invoiced' or 'draft'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', False):
                continue
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'agreement.rebate.settlement')
        return super(AgreementRebateSettlement, self).create(vals_list)

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order.
        This method may be overridden to implement custom invoice generation
        (making sure to call super() to establish a clean extension chain).
        """
        self.ensure_one()
        company_id = self.company_id.id or self.env.user.company_id.id
        partner = self.env.context.get('partner_invoice', self.partner_id)
        invoice_type = self.env.context.get('invoice_type', 'out_invoice')
        journal_id = (
            self.env.context.get('journal_id') or
            self.env['account.invoice'].with_context(
                company_id=company_id
            ).default_get(['journal_id'])['journal_id'])
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for'
                              ' this company.'))
        vinvoice = self.env['account.invoice'].new({
            'company_id': company_id,
            'partner_id': partner.id,
            'type': invoice_type,
            'journal_id': journal_id,
        })
        # Get partner extra fields
        vinvoice._onchange_partner_id()
        invoice_vals = vinvoice._convert_to_write(vinvoice._cache)
        invoice_vals.update({
            'name': (self.agreement_id.name or ''),
            'origin': self.name,
            'invoice_line_ids': [],
            'currency_id': partner.currency_id.id,
            # 'comment': self.note,
            # 'user_id': self.user_id and self.user_id.id,
            # 'team_id': self.team_id.id,
        })
        return invoice_vals

    def _prepare_invoice_line(self, settlement_line, invoice_vals):
        self.ensure_one()
        company_id = self.company_id.id or self.env.user.company_id.id
        product = self.env.context.get('product', False)
        invoice_line_vals = {
            # 'display_type': self.display_type,
            'product_id': product.id,
            'quantity': 1.0,
            'uom_id': product.uom_id.id,
        }
        invoice_line = self.env['account.invoice.line'].with_context(
            force_company=company_id,
        ).new(invoice_line_vals)
        invoice = self.env['account.invoice'].with_context(
            force_company=company_id,
        ).new(invoice_vals)
        invoice_line.invoice_id = invoice
        # Get other invoice line values from product onchange
        invoice_line._onchange_product_id()
        invoice_line_vals = invoice_line._convert_to_write(invoice_line._cache)
        invoice_line_vals.update({
            # 'account_analytic_id': self.analytic_account_id.id,
            # 'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'price_unit': settlement_line.amount_rebate,
        })
        return invoice_line_vals

    def _get_invoice_key(self):
        invoice_group = self.env.context.get('invoice_group', 'settlement')
        if invoice_group == 'settlement':
            return self.id
        if invoice_group == 'partner':
            return self.env.context.get('partner_id', self.partner_id.id)

    def create_invoice(self):
        invoice_dic = {}
        for settlement in self:
            key = settlement._get_invoice_key()
            if not key in invoice_dic:
                invoice_dic[key] = settlement._prepare_invoice()
            for line in settlement.line_ids:
                invoice_dic[key]['invoice_line_ids'].append(
                    (0, 0, settlement._prepare_invoice_line(
                        line, invoice_dic[key]))
                )
        invoices = self.env['account.invoice'].create(invoice_dic.values())
        return invoices

    def action_show_detail(self):
        if self.rebate_type == 'line' and len(self.line_ids) > 1:
            domain = expression.OR([safe_eval(
                l.target_domain) for l in self.line_ids])
        else:
            domain = safe_eval(self.line_ids[:1].target_domain)
        return {
            'name': _('Details'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice.report',
            'view_mode': 'pivot,tree',
            'domain': domain,
            'context': self.env.context,
        }

    def action_show_settlement(self):
        action = self.env.ref(
            'agreement_rebate.agreement_rebate_settlement_action').read()[0]
        if len(self) == 1:
            form = self.env.ref(
                'agreement_rebate.agreement_rebate_settlement_form')
            action['views'] = [(form.id, 'form')]
            action['res_id'] = self.id
        else:
            action['domain'] = [('id', 'in', self.ids)]
        return action

    def action_show_agreement(self):
        return self.agreement_id.get_formview_action()


class AgreementRebateSettlementLine(models.Model):
    _name = 'agreement.rebate.settlement.line'
    _description = 'Agreement Rebate Settlement Lines'

    rebate_settlement_id = fields.Many2one(
        comodel_name='agreement.rebate.settlement',
        string='Rebate settlement',
        ondelete='cascade',
    )
    rebate_line_id = fields.Many2one(
        comodel_name='agreement.rebate.line',
        string='Rebate Line',
    )
    rebate_section_id = fields.Many2one(
        comodel_name='agreement.rebate.section',
        string='Rebate section',
    )
    target_domain = fields.Char()
    amount_from = fields.Float(string="From", readonly=True)
    amount_to = fields.Float(string="To", readonly=True)
    percent = fields.Float(string="Percent", readonly=True)
    amount_gross = fields.Float(string='Amount gross')
    amount_invoiced = fields.Float(string='Amount invoiced')
    amount_rebate = fields.Float(string='Amount rebate')

    def action_show_detail(self):
        return {
            'name': _('Details'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice.line',
            'view_mode': 'tree',
            'domain': self.target_domain,
            'context': self.env.context,
        }
