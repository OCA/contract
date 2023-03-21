# Copyright 2023 Akretion - Florian Mounier
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.misc import formatLang


class ContractLinePriceHistory(models.Model):
    _name = "contract.line.price.history"
    _description = "Contract Line Price History"

    contract_line_id = fields.Many2one(
        comodel_name="contract.line",
        string="Contract Line",
        required=True,
        ondelete="cascade",
    )
    old_price = fields.Float(string="Old Price", required=False)
    new_price = fields.Float(string="New Price", required=True)
    type = fields.Selection(
        selection=[
            ("unknown", "?"),  # At module install or after sub module
            ("initial", "Initial"),
            ("update", "Update"),
            ("ui-update", "Manual Update"),
            ("revert", "Revert"),
        ],
        string="Type",
        default="unknown",
        required=True,
    )
    date = fields.Date(string="Date", required=True)

    price_display = fields.Char(
        string="Price",
        compute="_compute_price_display",
    )

    @api.depends("old_price", "new_price")
    def _compute_price_display(self):
        # Format the price to display it in the view
        for record in self:
            if record.type not in ["initial", "unknown"]:
                record.price_display = "{} -> {}".format(
                    formatLang(
                        record.env,
                        record.old_price,
                        monetary=True,
                        dp="Product Price",
                        currency_obj=record.contract_line_id.contract_id.currency_id,
                    ),
                    formatLang(
                        record.env,
                        record.new_price,
                        monetary=True,
                        dp="Product Price",
                        currency_obj=record.contract_line_id.contract_id.currency_id,
                    ),
                )
            else:
                record.price_display = formatLang(
                    record.env,
                    record.new_price,
                    monetary=True,
                    dp="Product Price",
                    currency_obj=record.contract_line_id.contract_id.currency_id,
                )

    def action_revert_price(self):
        # Revert the price of the contract line
        self.ensure_one()
        self.contract_line_id.with_context(price_unit_update_type="revert").write(
            {"price_unit": self.old_price}
        )
        return True
