# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict
from odoo import models, fields
from odoo.tools import safe_eval
from odoo.osv import expression


class AgreementSettlementInvoiceCreateWiz(models.TransientModel):
    _name = 'agreement.invoice.create.wiz'

    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    journal_type = fields.Selection(
        selection=[
            ('sale', 'Rebate Sales'),
        ],
        string='Journal type',
        default='sale',
    )
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

    def _prepare_settlement_domain(self):
        domain = [
            ('invoice_id', '=', False),
            ('agreement_id.rebate_type', '!=', False),
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
            domain.extend([('agreement_id', 'in', self.agreement_ids.ids)])
        elif self.agreement_type_ids:
            domain.extend([
                ('agreement_id.agreement_type_id', 'in',
                 self.agreement_type_ids.ids)
            ])
        else:
            domain.extend([
                ('agreement_id.agreement_type_id.journal_type', '=', self.journal_type),
            ])
        return domain

    def action_create_invoice(self):
        self.ensure_one()
        settlements = self.env['agreement.rebate.settlement'].search(
            self._prepare_settlement_domain())
        settlements.with_context(
            partner_invoice=self.invoice_partner_id,
            product=self.product_id,
            journal_id=self.journal_id.id,
            invoice_type=self.invoice_type,
            invoice_group=self.invoice_group,
        ).create_invoice()
