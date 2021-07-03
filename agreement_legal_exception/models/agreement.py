# Copyright 2021 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class Agreement(models.Model):
    _inherit = ["agreement", "base.exception"]
    _name = "agreement"
    _order = "main_exception_id asc, start_date desc, name desc"

    @api.model
    def detect_draft_exceptions(self):
        stage_ids = self._get_draft_stage_ids()
        agreement_set = self.search([("stage_id", "in", stage_ids)])
        agreement_set.detect_exceptions()
        return True

    @api.model
    def _reverse_field(self):
        return "agreement_ids"

    def detect_exceptions(self):
        all_exceptions = super().detect_exceptions()
        lines = self.mapped("line_ids")
        all_exceptions += lines.detect_exceptions()
        return all_exceptions

    @api.constrains("ignore_exception", "line_ids", "stage_id")
    def agreement_check_exception(self):
        stage_ids = self._get_reviewed_stage_ids()
        agreements = self.filtered(lambda s: s.stage_id.id in stage_ids)
        if agreements:
            agreements._check_exception()

    @api.onchange("line_ids")
    def onchange_ignore_exception(self):
        if self.stage_id.id in self._get_draft_stage_ids():
            self.ignore_exception = False

    def write(self, vals):
        # Fired as Reviewed
        if (
            vals.get("stage_id") in self._get_reviewed_stage_ids()
            and self.detect_exceptions()
        ):
            return self._fire_agreement_exception()
        result = super().write(vals)
        # Clared as set to draft
        if vals.get("stage_id") in self._get_draft_stage_ids():
            self._clear_agreement_exception()
        return result

    def _get_popup_action(self):
        return self.env.ref(
            "agreement_legal_exception.action_agreement_exception_confirm"
        )

    def _fire_agreement_exception(self):
        if self.detect_exceptions():
            return self._popup_exceptions()

    def _clear_agreement_exception(self):
        agreements = self.filtered("ignore_exception")
        agreements.write({"ignore_exception": False})

    def _get_draft_stage_ids(self):
        stages = [
            self.env.ref("agreement_legal.agreement_stage_new", False),
            self.env.ref("agreement_legal.agreement_stage_draft", False),
        ]
        return [stage.id for stage in stages if stage]

    def _get_reviewed_stage_ids(self):
        stages = [
            self.env.ref("agreement_legal.agreement_stage_reviewed", False),
            self.env.ref("agreement_legal.agreement_stage_active", False),
        ]
        return [stage.id for stage in stages if stage]
