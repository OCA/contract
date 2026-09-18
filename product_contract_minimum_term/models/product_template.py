# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError

CONTRACT_DURATION_TYPES = [
    ("fixed", "Fixed Duration"),
    ("minimum_term", "Minimum Term"),
]


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "contract.minimum.term.mixin"]

    contract_duration_type = fields.Selection(
        CONTRACT_DURATION_TYPES,
        string="Contract Duration",
        default="fixed",
        required=True,
        help="Fixed Duration: the contract line ends after the duration, it can "
        "be renewed automatically.\n"
        "Minimum Term: the contract line is open-ended, it cannot be "
        "terminated before the end of the minimum term, which is extended by "
        "the renewal term if the contract is not terminated in time.",
    )
    min_term_rule_type = fields.Selection(default="monthly")
    min_term_renewal_rule_type = fields.Selection(default="monthly")
    min_term_notice_rule_type = fields.Selection(default="monthly")

    @api.onchange("contract_duration_type")
    def _onchange_contract_duration_type(self):
        if self.contract_duration_type == "minimum_term":
            self.is_auto_renew = False

    @api.constrains("contract_duration_type", "is_auto_renew")
    def _check_contract_duration_type(self):
        for product in self:
            if product.contract_duration_type == "minimum_term" and (
                product.is_auto_renew
            ):
                raise ValidationError(
                    self.env._(
                        "The product %(product)s has a minimum term: it cannot "
                        "be renewed automatically.",
                        product=product.display_name,
                    )
                )
