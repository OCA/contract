# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ContractCheckout(models.TransientModel):

    _name = 'contract.checkout'
    _description = 'Contract Checkout'

    order_id = fields.Many2one(
        string='Order',
        comodel_name='sale.order',
        default=lambda s: s._default_order_id(),
    )
    temp_contract_ids = fields.One2many(
        string='Temp Contracts',
        comodel_name='contract.temp',
        inverse_name='contract_checkout_id',
    )
    partner_id = fields.Many2one(
        string='Customer',
        comodel_name='res.partner',
    )
    company_id = fields.Many2one(
        string='Customer Company',
        comodel_name='res.company',
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
    )

    @api.model
    def _default_order_id(self):
        if self.env.context.get('active_model') != 'sale.order':
            return
        return self.env['sale.order'].browse(
            self.env.context.get('active_id')
        )

    @api.model
    def search_checkout_detach_order(self, order):
        sale_lines = order.order_line.filtered(
            lambda s: s.product_id.is_contract
        )
        if not sale_lines:
            return False
        checkout = self.env['contract.checkout'].search([
            ('order_id', '=', order.id)
        ])
        if checkout:
            checkout.order_id = None

    @api.model
    def get_or_create_contract_checkout(self, order):
        """ Creates contract checkout with temp contracts dbl linked list """
        wizard = self.search([('order_id', '=', order.id)])
        if not wizard:
            wizard = self.create({
                'order_id': order.id,
                'partner_id': order.partner_id.id,
                'company_id': order.company_id.id,
                'currency_id': order.currency_id.id,
            })
            order_lines = order.order_line.filtered(
                lambda s: s.product_id.is_contract
            )
            wizard._create_contract_temp_linked_list(
                order_lines=order_lines,
            )
        return wizard

    @api.multi
    def _create_contract_temp_linked_list(self, order_lines):
        """ Converts order_lines to double linked list of contracts """
        self.ensure_one()
        ContractTemp = self.env['contract.temp']
        for line in order_lines:
            temp_contract = ContractTemp._convert_line_to_temp_contract(line)
            self._append_temp_contract_to_linked_list(temp_contract)

    @api.multi
    def _append_temp_contract_to_linked_list(self, temp_contract):
        """ Add temp contract to doubly linked list """
        self.ensure_one()
        temp_contract.ensure_one()
        if len(self.temp_contract_ids) > 0:
            self.temp_contract_ids[-1].next_contract_id = temp_contract
            temp_contract.previous_contract_id = self.temp_contract_ids[-1]
        self.write({
            'temp_contract_ids': [(4, temp_contract.id)],
        })

    @api.multi
    def convert_temp_contracts_to_accounts(self):
        """ Converts contract_ids to account.analytic.account """
        for record in self:
            record.temp_contract_ids._convert_to_analytic_account()
