# Copyright 2019 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Carlos Dauden
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ContractPriceRevisionWizard(models.TransientModel):
    """ Update contract price based on percentage variation """

    _name = "contract.price.revision.wizard"
    _description = "Wizard to update price based on percentage variation"

    date_start = fields.Date(required=True,)
    date_end = fields.Date()
    variation_type = fields.Selection(
        selection=lambda self: self._get_variation_type(),
        required=True,
        default=lambda self: self._get_default_variation_type(),
    )
    variation_percent = fields.Float(digits="Product Price", string="Variation %",)
    fixed_price = fields.Float(digits="Product Price")

    @api.model
    def _get_variation_type(self):
        return [
            ("percentage", "Percentage"),
            ("fixed", "Fixed Price"),
        ]

    @api.model
    def _get_default_variation_type(self):
        return "percentage"

    def _get_new_price(self, line):
        """Get the price depending the change type chosen
        """
        if self.variation_type == "percentage":
            return line.price_unit * (1.0 + self.variation_percent / 100.0)
        elif self.variation_type == "fixed":
            return self.fixed_price
        return line.price_unit

    def _get_new_line_value(self, line):
        self.ensure_one()
        return {
            "date_start": self.date_start,
            "last_date_invoiced": False,
            "date_end": self.date_end,
            "predecessor_contract_line_id": line.id,
            "price_unit": self._get_new_price(line),
        }

    def _get_old_line_date_end(self, line):
        return self.date_start - relativedelta(days=1)

    def action_apply(self):
        ContractLine = self.env["contract.line"]
        active_ids = self.env.context.get("active_ids")
        contracts = self.env["contract.contract"].browse(active_ids)
        for line in self._get_contract_lines_to_revise(contracts):
            date_end = self._get_old_line_date_end(line)
            line.stop(date_end)
            # As copy or copy_data are trigerring constraints, don't use them
            new_line = self.env["contract.line"].new(line._cache)
            new_line.update(self._get_new_line_value(line))
            new_line._onchange_date_start()
            new_line = ContractLine.create(new_line._convert_to_write(new_line._cache))
            line.update({"successor_contract_line_id": new_line.id})
        action = self.env["ir.actions.act_window"].for_xml_id(
            "contract", "action_customer_contract"
        )
        action["domain"] = [("id", "in", active_ids)]
        return action

    def _get_contract_lines_to_revise(self, contracts):
        self.ensure_one()
        to_revise = contracts.mapped("contract_line_ids").filtered(
            lambda x: not x.automatic_price
            and not x.successor_contract_line_id
            and x.recurring_next_date
            and (not x.date_end or x.date_end >= self.date_start)
        )
        return to_revise
