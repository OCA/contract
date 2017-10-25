# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import uuid

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class ContractTemp(models.TransientModel):

    _name = 'contract.temp'
    _description = 'Temporary Contract'

    name = fields.Char(
        string='Name',
    )
    contract_checkout_id = fields.Many2one(
        string='Contract Wizard',
        comodel_name='contract.checkout',
        ondelete='cascade',
    )
    signature_image = fields.Binary(
        string='Contract Signature',
        attachment=True,
    )
    signatory_name = fields.Char(
        string='Name of the signer',
    )
    accepted = fields.Boolean(
        string='Accepted Contract',
        compute='_compute_accepted',
    )
    contract_template_id = fields.Many2one(
        string='Contract Template',
        comodel_name='account.analytic.contract',
    )
    website_template_id = fields.Many2one(
        string='Contract Website Template',
        comodel_name='account.analytic.contract.template',
        compute='_compute_website_template_id',
        store=True,
    )
    next_contract_id = fields.Many2one(
        string='Next Contract',
        comodel_name='contract.temp',
    )
    previous_contract_id = fields.Many2one(
        string='Previous Contract',
        comodel_name='contract.temp',
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
    )
    access_token = fields.Char(
        string='Security Token',
        copy=False,
        required=True,
        default=lambda s: str(uuid.uuid4()),
    )
    website_url = fields.Char(
        string='Website URL',
        required=True,
        compute='_compute_website_url',
    )
    partner_id = fields.Many2one(
        string='Customer',
        related='contract_checkout_id.partner_id',
    )
    company_id = fields.Many2one(
        string='Company',
        related='contract_checkout_id.company_id',
    )
    currency_id = fields.Many2one(
        string='Currency',
        related='contract_checkout_id.currency_id',
    )
    contract_fee = fields.Monetary(
        string='Setup Fee',
        help='Cost of initializing contract. Directly '
             'taken from the total cost of the related '
             'product.'
    )
    order_line_id = fields.Many2one(
        string='Order Line',
        comodel_name='sale.order.line',
        required=True,
    )

    @api.multi
    def get_previous_unsigned_contracts(self):
        self.ensure_one()
        contracts = self.contract_checkout_id.temp_contract_ids
        unsigned = self.browse()
        for contract in contracts:
            if contract.id == self.id:
                break
            if not contract.accepted:
                unsigned += contract
        return unsigned

    @api.multi
    def _compute_website_url(self):
        for record in self:
            record.website_url = '/shop/checkout/contract/%d/%s' % (
                record.id, record.access_token,
            )

    @api.multi
    @api.depends('signature_image', 'signatory_name')
    def _compute_accepted(self):
        for record in self:
            record.accepted = bool(
                record.signature_image and record.signatory_name
            )

    @api.multi
    @api.depends(
        'contract_template_id', 'contract_template_id.website_template_id')
    def _compute_website_template_id(self):
        for record in self:
            if record.contract_template_id.website_template_id:
                record.website_template_id = \
                    record.contract_template_id.website_template_id
            else:
                Contract = self.env['account.analytic.contract']
                record.website_template_id = Contract._get_default_template()

    @api.model
    def _convert_line_to_temp_contract(self, order_line):
        order_line.ensure_one()
        contract_template = order_line.product_id.contract_template_id
        vals = {
            'name': order_line.product_id.name,
            'contract_template_id': contract_template.id,
            'product_id': order_line.product_id.id,
            'order_line_id': order_line.id,
            'contract_fee': order_line.price_total,
        }
        return self.env['contract.temp'].create(vals)
