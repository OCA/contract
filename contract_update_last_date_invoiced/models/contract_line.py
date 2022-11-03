# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class ContractLine(models.Model):

    _inherit = "contract.line"

    def action_update_last_date_invoiced(self):
        self.ensure_one()
        context = {
            "default_contract_line_id": self.id,
            "default_last_date_invoiced": self.last_date_invoiced,
            "default_recurring_next_date": self.recurring_next_date,
        }
        context.update(self.env.context)
        return {
            "type": "ir.actions.act_window",
            "name": _("Update Last Date Invoiced"),
            "res_model": "contract.update.last.date.invoiced",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "context": context,
        }

    def _update_last_date_invoiced(self, last_date_invoiced, recurring_next_date):
        self.write(
            {
                "last_date_invoiced": last_date_invoiced,
                "recurring_next_date": recurring_next_date,
            }
        )
