# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields


class AgreementSettlementInvoiceCreateWiz(models.TransientModel):
    _name = 'agreement.invoice.create.wiz'

    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    domain = fields.Selection(
        '_domain_selection', string='Domain', default='sale')
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        required=True,
    )
    agreement_type_ids = fields.Many2many(
        comodel_name='agreement.type',
        string='Agreement types',
    )
    agreement_ids = fields.Many2many(
        comodel_name='agreement',
        string='Agreements',
    )
    settlements_ids = fields.Many2many(
        comodel_name='agreement.rebate.settlement',
        string='Rebate settlements',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
    )
    invoice_group = fields.Selection([
        ('settlement', 'Settlement'),
        ('partner', 'Partner')
        ],
        required=True,
        default='settlement',
        string='Group invoice by',
    )
    invoice_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Force invoice to'
    )
    invoice_type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill'),
        ('out_refund', 'Customer Credit Note'),
        ('in_refund', 'Vendor Credit Note')],
        required=True,
        default='out_invoice',
    )

    @api.model
    def _domain_selection(self):
        return self.env['agreement']._domain_selection()

    def _prepare_settlement_domain(self):
        domain = [
            ('line_ids.invoice_line_id', '=', False),
            ('line_ids.rebate_type', '!=', False),
        ]
        if self.date_from:
            domain.extend([
                ('date_to', '>=', self.date_from),
            ])
        if self.date_to:
            domain.extend([
                ('date_to', '<=', self.date_to),
            ])
        if self.settlements_ids:
            domain.extend([('id', 'in', self.settlements_ids.ids)])
        elif self.agreement_ids:
            domain.extend([
                ('line_ids.agreement_id', 'in', self.agreement_ids.ids)])
        elif self.agreement_type_ids:
            domain.extend([
                ('line_ids.agreement_id.agreement_type_id', 'in',
                 self.agreement_type_ids.ids)
            ])
        else:
            domain.extend([
                ('line_ids.agreement_id.agreement_type_id.domain',
                 '=', self.domain),
            ])
        return domain

    def action_create_invoice(self):
        self.ensure_one()
        settlements = self.env['agreement.rebate.settlement'].search(
            self._prepare_settlement_domain())
        invoices = settlements.with_context(
            partner_invoice=self.invoice_partner_id,
            product=self.product_id,
            journal_id=self.journal_id.id,
            invoice_type=self.invoice_type,
            invoice_group=self.invoice_group,
            date_from=self.date_from,
            date_to=self.date_to,
        ).create_invoice()
        return self.action_show_invoices(invoices)

    def action_show_invoices(self, invoices):
        self.ensure_one()
        tree_view_ref = (
            'account.invoice_supplier_tree'
            if 'in_' in self.invoice_type
            else 'account.invoice_tree_with_onboarding'
        )
        form_view_ref = (
            'account.invoice_supplier_form'
            if 'in_' in self.invoice_type
            else 'account.invoice_form'
        )
        tree_view = self.env.ref(tree_view_ref, raise_if_not_found=False)
        form_view = self.env.ref(form_view_ref, raise_if_not_found=False)
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.invoice',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
            'domain': [('id', 'in', invoices.ids)],
        }
        if tree_view and form_view:
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
        return action
