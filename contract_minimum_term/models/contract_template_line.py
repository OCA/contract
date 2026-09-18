# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ContractTemplateLine(models.Model):
    _name = "contract.template.line"
    _inherit = ["contract.template.line", "contract.minimum.term.mixin"]

    # Like the recurrence fields, the minimum term is taken from the contract
    # unless the recurrence is managed at line level. One compute method per
    # field, so that a value given at creation only protects its own field.
    min_term_interval = fields.Integer(
        compute="_compute_min_term_interval", store=True, readonly=False
    )
    min_term_rule_type = fields.Selection(
        compute="_compute_min_term_rule_type", store=True, readonly=False
    )
    min_term_renewal_interval = fields.Integer(
        compute="_compute_min_term_renewal_interval", store=True, readonly=False
    )
    min_term_renewal_rule_type = fields.Selection(
        compute="_compute_min_term_renewal_rule_type", store=True, readonly=False
    )
    min_term_notice_interval = fields.Integer(
        compute="_compute_min_term_notice_interval", store=True, readonly=False
    )
    min_term_notice_rule_type = fields.Selection(
        compute="_compute_min_term_notice_rule_type", store=True, readonly=False
    )

    def _set_min_term_field(self, field_name):
        for record in self:
            if not record.contract_id.line_recurrence:
                record[field_name] = record.contract_id[field_name]
            elif self._fields[field_name].type == "selection":
                # Keep the line value, the contract one as default
                record[field_name] = (
                    record[field_name] or record.contract_id[field_name]
                )
            else:
                record[field_name] = record[field_name]

    @api.depends("contract_id.min_term_interval", "contract_id.line_recurrence")
    def _compute_min_term_interval(self):
        self._set_min_term_field("min_term_interval")

    @api.depends("contract_id.min_term_rule_type", "contract_id.line_recurrence")
    def _compute_min_term_rule_type(self):
        self._set_min_term_field("min_term_rule_type")

    @api.depends("contract_id.min_term_renewal_interval", "contract_id.line_recurrence")
    def _compute_min_term_renewal_interval(self):
        self._set_min_term_field("min_term_renewal_interval")

    @api.depends(
        "contract_id.min_term_renewal_rule_type", "contract_id.line_recurrence"
    )
    def _compute_min_term_renewal_rule_type(self):
        self._set_min_term_field("min_term_renewal_rule_type")

    @api.depends("contract_id.min_term_notice_interval", "contract_id.line_recurrence")
    def _compute_min_term_notice_interval(self):
        self._set_min_term_field("min_term_notice_interval")

    @api.depends("contract_id.min_term_notice_rule_type", "contract_id.line_recurrence")
    def _compute_min_term_notice_rule_type(self):
        self._set_min_term_field("min_term_notice_rule_type")

    @api.constrains("min_term_interval", "is_auto_renew")
    def _check_min_term_auto_renew(self):
        """A minimum term keeps the line open-ended: it cannot be combined with
        a fixed end date renewed automatically."""
        for record in self:
            if record.min_term_interval > 0 and record.is_auto_renew:
                raise ValidationError(
                    self.env._(
                        "The line %(line)s cannot have both a minimum term and "
                        "an automatic renewal.",
                        line=record.name,
                    )
                )
