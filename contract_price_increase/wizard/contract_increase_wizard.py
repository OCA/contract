from odoo import fields, models


class ContractIncreaseWizard(models.TransientModel):
    _name = "contract.increase.wizard"

    date = fields.Date(string="Date of increase", required=True)
    rate = fields.Float(string="Rate of increase", required=True)
    description = fields.Text(string="Description")

    def increase(self):
        """Add an increase to a contract."""

        contracts = self.env["contract.contract"].browse(
            self._context.get("active_ids")
        )
        contracts._create_increase(self.date, self.rate, self.description)

        return True
