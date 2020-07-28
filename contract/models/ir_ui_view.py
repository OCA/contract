# Copyright 2020 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    @api.model
    def _prepare_qcontext(self):
        """Patch context to use fw-compatible v13 company."""
        # TODO Delete this method in v13; it's upstream there
        result = super()._prepare_qcontext()
        if self.env.context.get("allowed_company_ids"):
            result["res_company"] = self.env["res.company"].browse(
                self.env.context["allowed_company_ids"][0]
            ).sudo()
        return result
