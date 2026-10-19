# Copyright 2026 Cristiano Mafra Junior - Escodoo <https://escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    contract_count = fields.Integer(
        string="# Contracts", compute="_compute_contract_count"
    )

    @api.depends("analytic_account_id")
    def _compute_contract_count(self):
        if not self.analytic_account_id:
            self.contract_count = 0
            return
        query = self.env["contract.line"]._search([])
        query.add_where(
            "contract_line.analytic_distribution ?| %s",
            [[str(account_id) for account_id in self.analytic_account_id.ids]],
        )
        query.order = None
        query_string, query_param = query.select(
            "jsonb_object_keys(contract_line.analytic_distribution) as account_id",
            "COUNT(DISTINCT(contract_id)) as contract_count",
        )
        query_string = (
            f"{query_string} GROUP BY "
            "jsonb_object_keys(contract_line.analytic_distribution)"
        )
        self._cr.execute(query_string, query_param)
        data = {
            int(record.get("account_id")): record.get("contract_count")
            for record in self._cr.dictfetchall()
        }
        for project in self:
            project.contract_count = data.get(project.analytic_account_id.id, 0)

    def action_open_project_contracts(self):
        self.ensure_one()
        query = self.env["contract.line"]._search([])
        query.add_where(
            "contract_line.analytic_distribution ? %s",
            [str(self.analytic_account_id.id)],
        )
        query_string, query_param = query.select("contract_id")
        self._cr.execute(query_string, query_param)
        contract_ids = [line.get("contract_id") for line in self._cr.dictfetchall()]
        action_window = {
            "name": _("Contracts"),
            "type": "ir.actions.act_window",
            "res_model": "contract.contract",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [("id", "in", contract_ids)],
        }
        if len(contract_ids) == 1:
            action_window["views"] = [[False, "form"]]
            action_window["res_id"] = contract_ids[0]
        return action_window
