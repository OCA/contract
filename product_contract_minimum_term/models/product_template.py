# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

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
        help="Fixed Duration: the contract line ends after the duration, and "
        "is renewed with a new end date when it is set to auto renew.\n"
        "Minimum Term: the contract line is open-ended, it cannot be "
        "terminated before the end of the minimum term. When it is set to "
        "auto renew, the minimum term itself is renewed if the contract is "
        "not terminated within the termination notice.",
    )
    min_term_rule_type = fields.Selection(default="monthly")
