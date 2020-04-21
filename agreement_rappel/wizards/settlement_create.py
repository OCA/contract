# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict
from odoo import models, fields
from odoo.tools import safe_eval
from odoo.osv import expression


class AgreementSettlementCreateWiz(models.TransientModel):
    _name = 'agreement.settlement.create.wiz'

    date = fields.Date(default=fields.Date.today())
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To', required=True)
    journal_type = fields.Selection(
        selection=[
            ('sale', 'Rappel Sales'),
        ],
        string='Journal type',
        default='sale',
    )
    journal_ids = fields.Many2many(
        comodel_name='account.journal',
        string='Journals',
    )
    agreement_type_ids = fields.Many2many(
        comodel_name='agreement.type',
        string='Agreement types',
    )
    agreement_ids = fields.Many2many(
        comodel_name='agreement',
        string='Agreements',
    )

    def _prepare_agreement_domain(self):
        domain = [
            ('rappel_type', '!=', False),
        ]
        settlement_domain = []
        if self.date_from:
            settlement_domain.extend([
                ('date_to', '>=', self.date_from),
            ])
        if self.date_to:
            settlement_domain.extend([
                ('date_to', '<=', self.date_to),
            ])
        if self.agreement_ids:
            domain.extend([('id', 'in', self.agreement_ids.ids)])
            settlement_domain.extend([
                ('agreement_id', 'in', self.agreement_ids.ids),
            ])
        elif self.agreement_type_ids:
            domain.extend([
                ('agreement_type_id', 'in', self.agreement_type_ids.ids)
            ])
            settlement_domain.extend([
                ('agreement_id.agreement_type_id', 'in',
                 self.agreement_type_ids.ids)
            ])
        else:
            domain.extend([
                ('agreement_type_id.journal_type', '=', self.journal_type),
            ])
        settlements = self._get_existing_settlement(settlement_domain)
        if settlements:
            domain.extend([
                ('id', 'not in', settlements.mapped('agreement_id').ids)
            ])
        return domain

    def _get_existing_settlement(self, domain):
        return self.env['agreement.rappel.settlement'].search(domain)

    def _get_target_model(self):
        return self.env['account.invoice.line']

    def _prepare_target_domain(self):
        domain = []
        if self.journal_ids:
            domain.extend([
                ('invoice_id.journal_id', 'in', self.journal_ids.ids),
            ])
        else:
            domain.extend([
                ('invoice_id.journal_id.type', '=', self.journal_type),
            ])
        if self.date_from:
            domain.extend([
                ('invoice_id.date_invoice', '>=', fields.Date.to_string(
                    self.date_from)),
            ])
        if self.date_to:
            domain.extend([
                ('invoice_id.date_invoice', '<=', fields.Date.to_string(
                    self.date_to)),
            ])
        return domain

    def _target_line_domain(self, agreement_domain, agreement, line=False):
        if line:
            return agreement_domain + safe_eval(line.rappel_domain)
        if agreement.rappel_line_ids:
            domain = expression.OR(
                [safe_eval(l.rappel_domain) for l in agreement.rappel_line_ids]
            )
            return expression.AND([agreement_domain, domain])
        return agreement_domain

    def get_agregate_fields(self):
        return ['price_unit', 'price_subtotal', 'price_subtotal_signed',
                'price_total', 'price_tax']

    def _get_amount_field(self):
        return 'price_total'

    def _prepare_settlement_line(
        self, domain, groups, agreement, line=False, section=False):
        amount = groups[0][self._get_amount_field()]
        vals = {
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        if agreement.rappel_type == 'line':
            rappel = amount * line.rappel_discount / 100
            vals.update({
                'rappel_line_id': line.id,
                'percent': line.rappel_discount,
            })
        elif agreement.rappel_type == 'section_prorated':
            if amount >= section.amount_to:
                amount_section = section.amount_to
            elif amount >= section.amount_from:
                amount_section = amount - section.amount_from
            rappel = amount_section * section.rappel_discount / 100
            vals.update({
                'rappel_section_id': section.id,
                'amount_from': section.amount_from,
                'amount_to': section.amount_to,
                'percent': section.rappel_discount,
            })
        elif agreement.rappel_type == 'global':
            rappel = amount * agreement.rappel_discount / 100
            vals.update({
                'percent': agreement.rappel_discount,
            })
        elif agreement.rappel_type == 'section_total':
            section = agreement.rappel_section_ids.filtered(
                lambda s: s.amount_from <= amount <= s.amount_to)
            rappel = amount * section.rappel_discount / 100
            vals.update({
                'percent': section.rappel_discount,
                'amount_from': section.amount_from,
                'amount_to': section.amount_to,
            })
        vals.update({
            'target_domain': domain,
            'amount_invoiced': agreement.company_id.currency_id.round(amount),
            'amount_rappel': agreement.company_id.currency_id.round(rappel),
        })
        return vals

    def _get_rappel_discount(self, agreement, amount):
        if agreement.rappel_type == 'global':
            return agreement.rappel_discount
        if agreement.rappel_type == 'section_total':
            section = agreement.rappel_section_ids.filtered(
                lambda s: s.amount_from <= amount <= s.amount_to)
            return section.rappel_discount

    def _partner_domain(self, agreement):
        return [
            ('invoice_id.partner_id', 'child_of', agreement.partner_id.ids),
        ]

    def action_create_settlement(self):
        self.ensure_one()
        Agreement = self.env['agreement']
        target_model = self._get_target_model()
        orig_domain = self._prepare_target_domain()
        settlement_dic = defaultdict(lambda: {
            'lines': [],
        })
        agreements = Agreement.search(self._prepare_agreement_domain())
        for agreement in agreements:
            rappel = amount = total_rappel = total_amount = 0.0
            agreement_domain = orig_domain + self._partner_domain(agreement)
            if agreement.rappel_type == 'line':
                if not agreement.rappel_line_ids:
                    continue
                for line in agreement.rappel_line_ids:
                    domain = self._target_line_domain(
                        agreement_domain, agreement, line=line)
                    groups = target_model.read_group(
                        domain, self.get_agregate_fields(), [])
                    if not groups[0]['__count']:
                        continue
                    vals = self._prepare_settlement_line(
                        domain, groups, agreement, line=line)
                    total_rappel += vals['amount_rappel']
                    total_amount += vals['amount_invoiced']
                    settlement_dic[agreement]['lines'].append((0, 0, vals))
            elif agreement.rappel_type == 'section_prorated':
                domain = self._target_line_domain(agreement_domain, agreement)
                groups = target_model.read_group(
                    domain, self.get_agregate_fields(), [])
                if not groups[0]['__count']:
                    continue
                amount = groups and groups[0][self._get_amount_field()] or 0.0
                for section in agreement.rappel_section_ids:
                    if (amount < section.amount_to and amount <
                            section.amount_from):
                        break
                    vals = self._prepare_settlement_line(
                        domain, groups, agreement, section=section)
                    total_rappel += vals['amount_rappel']
                    settlement_dic[agreement]['lines'].append((0, 0, vals))
            else:
                domain = self._target_line_domain(agreement_domain, agreement)
                groups = target_model.read_group(
                    domain, self.get_agregate_fields(), [])
                if not groups[0]['__count']:
                    continue
                vals = self._prepare_settlement_line(domain, groups, agreement)
                settlement_dic[agreement]['lines'].append((0, 0, vals))

            settlement_dic[agreement]['amount_rappel'] = (
                total_rappel or vals['amount_rappel'])
            settlement_dic[agreement]['amount_invoiced'] = (
                total_amount or vals['amount_invoiced'])
        settlements = self._create_settlement(settlement_dic)
        return settlements.action_show_settlement()

    def _filter_settlement_lines(self, settlement_lines):
        return [line for line in filter(
            lambda l: l[2]['amount_rappel'] > 0.0, settlement_lines)]

    def _prepare_settlement(self, agreement, settlement_lines):
        lines = self._filter_settlement_lines(settlement_lines['lines'])
        if not lines:
            return {}
        return {
            'date': self.date,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'agreement_id': agreement.id,
            'line_ids': lines,
            'amount_rappel': settlement_lines['amount_rappel'],
            'amount_invoiced': settlement_lines['amount_invoiced'],
        }

    def _create_settlement(self, settlements):
        vals_list = []
        for agreement, settlement_lines in settlements.items():
            vals = self._prepare_settlement(agreement, settlement_lines)
            if vals:
                vals_list.append(vals)
        return self.env['agreement.rappel.settlement'].create(vals_list)
