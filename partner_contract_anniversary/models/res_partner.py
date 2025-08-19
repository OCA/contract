# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    first_contract_line_start_date = fields.Date(string="First Contract Date")
    contract_anniversary_date = fields.Date()

    def _update_contract_anniversary(self, partner_ids=None):
        def _anniv(d: date, year: int) -> date:
            try:
                return d.replace(year=year)
            except ValueError:
                return date(year, 2, 28)

        domain = [("is_canceled", "!=", True)]
        if partner_ids:
            domain.append(("partner_id", "in", partner_ids))
        groups = self.env["contract.line"].read_group(
            domain=[("is_canceled", "!=", True)],
            fields=["date_start:min", "partner_id"],
            groupby=["partner_id"],
        )
        first_start = {
            g["partner_id"][0]: fields.Date.to_date(g["date_start"])
            for g in groups
            if g.get("date_start")
        }
        this_year = fields.Date.context_today(self).year
        for p in self.env["res.partner"].browse(partner_ids):
            d0 = first_start.get(p.id)
            anniv = _anniv(d0, this_year) if d0 else False
            p.write(
                {
                    "first_contract_line_start_date": d0,
                    "contract_anniversary_date": anniv,
                }
            )

    def _cron_update_contract_anniversary(self):
        self._update_contract_anniversary()
