# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class ContractManuallySingleInvoice(models.TransientModel):
    _name = "contract.manually.single.invoice"
    _description = "Manually invoice a single contract"

    contract_id = fields.Many2one("contract.contract", required=True)
    date = fields.Date(required=True, default=lambda r: fields.Date.today())

    def create_invoice(self):
        while (
            self.contract_id.recurring_next_date
            and self.contract_id.recurring_next_date <= self.date
            and (
                not self.contract_id.date_end
                or self.contract_id.recurring_next_date <= self.contract_id.date_end
            )
        ):
            result = (
                self.env["contract.contract"]
                .with_company(self.contract_id.company_id.id)
                ._cron_recurring_create(
                    self.contract_id.recurring_next_date,
                    create_type=self.contract_id.generation_type,
                    domain=[("id", "=", self.contract_id.id)],
                )
            )
            for record in result:
                self.contract_id.message_post(
                    body=_(
                        "Contract manually generated: "
                        '<a href="#" data-oe-model="%s" data-oe-id="%s">'
                        "%s"
                        "</a>"
                    )
                    % (record._name, record.id, record.display_name)
                )
        return True
