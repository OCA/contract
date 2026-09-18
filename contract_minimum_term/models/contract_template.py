# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractTemplate(models.Model):
    _name = "contract.template"
    _inherit = ["contract.template", "contract.minimum.term.mixin"]

    # Defaults only at contract level: the line values are computed from the
    # contract unless the recurrence is managed at line level.
    min_term_rule_type = fields.Selection(default="monthly")
    min_term_renewal_rule_type = fields.Selection(default="monthly")
    min_term_notice_rule_type = fields.Selection(default="monthly")
