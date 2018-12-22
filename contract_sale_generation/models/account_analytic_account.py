# -*- coding: utf-8 -*-
# © 2004-2010 OpenERP SA
# © 2014 Angel Moya <angel.moya@domatix.com>
# © 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# Copyright 2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _prepare_sale_line(self, line, order_id):
        sale_line = self.env['sale.order.line'].new({
            'order_id': order_id,
            'product_id': line.product_id.id,
            'product_qty': line.quantity,
            'product_uom_qty': line.quantity,
            'product_uom': line.uom_id.id,
        })
        # Get other sale line values from product onchange
        sale_line.product_id_change()
        sale_line_vals = sale_line._convert_to_write(sale_line._cache)
        # Insert markers
        name = self._insert_markers(line.name)
        sale_line_vals.update({
            'name': name,
            'discount': line.discount,
            'price_unit': line.price_unit,
        })
        return sale_line_vals

    @api.multi
    def _prepare_sale(self):
        self.ensure_one()
        if not self.partner_id:
            raise ValidationError(
                _("You must first select a Customer for Contract %s!") %
                self.name)
        sale = self.env['sale.order'].new({
            'partner_id': self.partner_id,
            'date_order': self.recurring_next_date,
            'origin': self.name,
            'company_id': self.company_id.id,
            'user_id': self.partner_id.user_id.id,
            'project_id': self.id
        })
        # Get other invoice values from partner onchange
        sale.onchange_partner_id()
        return sale._convert_to_write(sale._cache)

    @api.multi
    def _create_invoice(self):
        """
        Create invoices
        @param self: single record of account.invoice
        @return: MUST return an invoice recordset
        """
        self.ensure_one()
        if self.type == 'invoice':
            return super(AccountAnalyticAccount, self)._create_invoice()
        else:
            return self.env['account.invoice']

    @api.multi
    def _create_sale(self):
        """
        Create Sale orders
        @param self: single record of sale.order
        @return: MUST return a sale.order recordset
        """
        self.ensure_one()
        if self.type == 'sale':
            sale_vals = self._prepare_sale()
            sale = self.env['sale.order'].create(sale_vals)
            for line in self.recurring_invoice_line_ids:
                sale_line_vals = self._prepare_sale_line(line, sale.id)
                self.env['sale.order.line'].create(sale_line_vals)
            if self.sale_autoconfirm:
                sale.action_confirm()
            return sale
        else:
            return self.env['sale.order']

    @api.multi
    def recurring_create_sale(self):
        """
        Create sales from contracts
        :return: sales created
        """
        sales = self.env['sale.order']
        for contract in self:
            if not contract.check_dates_valid():
                continue
            # Re-read contract with correct company
            ctx = contract.get_invoice_context()
            sales |= contract.with_context(ctx)._create_sale()
            contract.write({
                'recurring_next_date': fields.Date.to_string(ctx['next_date'])
            })
        return sales

    @api.model
    def cron_recurring_create_sale(self):
        today = fields.Date.today()
        contracts = self.search([
            ('recurring_invoices', '=', True),
            ('recurring_next_date', '<=', today),
            '|',
            ('date_end', '=', False),
            ('date_end', '>=', today),
        ])
        return contracts.recurring_create_sale()
