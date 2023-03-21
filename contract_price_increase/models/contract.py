# Copyright 2023 Akretion - Florian Mounier
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    increase_ids = fields.One2many(
        comodel_name="contract.increase",
        inverse_name="contract_id",
        string="Increases",
    )

    has_increases = fields.Boolean(
        string="Has Increases",
        compute="_compute_has_increases",
        store=True,
    )

    @api.depends("increase_ids")
    def _compute_has_increases(self):
        for contract in self:
            contract.has_increases = bool(contract.increase_ids)

    def _create_increase(self, date, rate, description):
        for contract in self:
            contract.increase_ids.create(
                {
                    "contract_id": contract.id,
                    "date": date,
                    "rate": rate,
                    "description": description,
                }
            )

    def _apply_increase(self, increase):
        self.ensure_one()
        for line in self.contract_line_ids:
            line.price_unit *= 1 + increase.rate

    def _apply_increases(self, date):
        for contract in self:
            relevant_increases = contract.increase_ids.filtered(
                lambda i: i.date <= date and not i.application_date
            )
            for increase in relevant_increases.sorted(key=lambda i: i.date):
                contract._apply_increase(increase)
                increase.application_date = date

    def cron_apply_increases(self):
        domain = self._get_contracts_to_increase_domain()
        relevant_contracts = self.search(domain)
        relevant_contracts._apply_increases(fields.Date.today())

    def _get_contracts_to_increase_domain(self):
        return [
            ("increase_ids.date", "<=", fields.Date.today()),
            ("increase_ids.application_date", "=", False),
        ]
