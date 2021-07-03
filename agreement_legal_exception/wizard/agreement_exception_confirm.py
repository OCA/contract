# Copyright 2021 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AgreementExceptionConfirm(models.TransientModel):
    _name = "agreement.exception.confirm"
    _description = "agreement exception wizard"
    _inherit = ["exception.rule.confirm"]

    related_model_id = fields.Many2one("agreement", "Agreement")

    def action_confirm(self):
        self.ensure_one()
        if self.ignore:
            self.related_model_id._clear_agreement_exception()
            self.related_model_id.ignore_exception = True
        return super().action_confirm()
