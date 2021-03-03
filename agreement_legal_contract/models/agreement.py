# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from ast import literal_eval

from odoo import fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    contract_type = fields.Selection(
        selection=[("sale", "Customer"), ("purchase", "Supplier")],
    )
    contract_count = fields.Integer(
        compute="_compute_contract_count",
        string="Contract Count",
        compute_sudo=True,
    )

    def _get_contract(self):
        contracts = self.env["contract.contract"].search(
            [("agreement_id", "=", self.id)]
        )
        return contracts

    def _compute_contract_count(self):
        self.contract_count = len(self._get_contract())

    def view_contract(self):
        self.ensure_one()
        xml_id = (
            self.contract_type == "purchase"
            and "contract.action_supplier_contract"
            or "contract.action_customer_contract"
        )
        action = self.env["ir.actions.act_window"]._for_xml_id(xml_id)
        context = literal_eval(action["context"].strip())
        context.pop("search_default_not_finished", None)
        action.update(
            {
                "domain": [("id", "in", self._get_contract().ids)],
                "context": context,
            }
        )
        return action
