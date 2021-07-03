# Copyright 2021 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AgreementLine(models.Model):
    _inherit = ["agreement.line", "base.exception.method"]
    _name = "agreement.line"

    ignore_exception = fields.Boolean(
        related="agreement_id.ignore_exception", store=True, string="Ignore Exceptions"
    )

    def _get_main_records(self):
        return self.mapped("agreement_id")

    @api.model
    def _reverse_field(self):
        return "agreement_ids"

    def _detect_exceptions(self, rule):
        records = super()._detect_exceptions(rule)
        return records.mapped("agreement_id")
