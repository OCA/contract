# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.contract_minimum_term.models.contract_minimum_term_mixin import (
    MINIMUM_TERM_FIELDS,
)

from .product_template import CONTRACT_DURATION_TYPES


class SaleOrderLineContractMixin(models.AbstractModel):
    _name = "sale.order.line.contract.mixin"
    _inherit = ["sale.order.line.contract.mixin", "contract.minimum.term.mixin"]

    contract_duration_type = fields.Selection(
        CONTRACT_DURATION_TYPES,
        string="Contract Duration",
        compute="_compute_product_contract_minimum_term",
        precompute=True,
        store=True,
        readonly=False,
    )
    min_term_interval = fields.Integer(
        compute="_compute_product_contract_minimum_term",
        precompute=True,
        store=True,
        readonly=False,
    )
    min_term_rule_type = fields.Selection(
        compute="_compute_product_contract_minimum_term",
        precompute=True,
        store=True,
        readonly=False,
    )
    min_term_renewal_interval = fields.Integer(
        compute="_compute_product_contract_minimum_term",
        precompute=True,
        store=True,
        readonly=False,
    )
    min_term_renewal_rule_type = fields.Selection(
        compute="_compute_product_contract_minimum_term",
        precompute=True,
        store=True,
        readonly=False,
    )
    min_term_notice_interval = fields.Integer(
        compute="_compute_product_contract_minimum_term",
        precompute=True,
        store=True,
        readonly=False,
    )
    min_term_notice_rule_type = fields.Selection(
        compute="_compute_product_contract_minimum_term",
        precompute=True,
        store=True,
        readonly=False,
    )

    @api.depends("product_id")
    def _compute_product_contract_minimum_term(self):
        for rec in self:
            product = rec.product_id
            if not product.is_contract:
                rec.contract_duration_type = False
                rec.update(dict.fromkeys(MINIMUM_TERM_FIELDS, False))
                continue
            rec.contract_duration_type = product.contract_duration_type
            rec.update({fname: product[fname] for fname in MINIMUM_TERM_FIELDS})

    def _is_contract_minimum_term(self):
        self.ensure_one()
        return self.is_contract and self.contract_duration_type == "minimum_term"

    @api.onchange("contract_duration_type")
    def _onchange_contract_duration_type(self):
        if self.contract_duration_type == "minimum_term":
            self.is_auto_renew = False

    @api.depends("contract_duration_type")
    def _compute_contract_line_date_end(self):
        res = super()._compute_contract_line_date_end()
        for rec in self:
            if rec._is_contract_minimum_term():
                rec.date_end = False
        return res
