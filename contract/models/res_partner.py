# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_contract_count = fields.Integer(
        string="Sale Contracts",
        compute="_compute_contract_count",
    )
    purchase_contract_count = fields.Integer(
        string="Purchase Contracts",
        compute="_compute_contract_count",
    )
    contract_ids = fields.One2many(
        comodel_name="contract.contract",
        inverse_name="partner_id",
        string="Contracts",
    )

    def _get_partner_contract_domain(self):
        return [("partner_id", "child_of", self.ids)]

    def _compute_contract_count(self):
        contract_model = self.env["contract.contract"]
        fetch_data = contract_model.formatted_read_group(
            domain=[("partner_id", "in", self.ids)],
            groupby=["partner_id", "contract_type"],
            aggregates=["__count"],
        )
        for partner in self:
            partner_child_ids = partner.child_ids.ids + partner.ids
            partner.sale_contract_count = sum(
                d["__count"]
                for d in fetch_data
                if d["partner_id"][0] in partner_child_ids
                and d["contract_type"] == "sale"
            )
            partner.purchase_contract_count = sum(
                d["__count"]
                for d in fetch_data
                if d["partner_id"][0] in partner_child_ids
                and d["contract_type"] == "purchase"
            )

    def act_show_contract(self):
        """This opens contract view
        @return: the contract view
        """
        self.ensure_one()
        contract_type = self.env.context.get("contract_type")

        res = self._get_act_window_contract_xml(contract_type)
        action_context = {k: v for k, v in self.env.context.items() if k != "group_by"}
        action_context["default_partner_id"] = self.id
        action_context["default_pricelist_id"] = self.property_product_pricelist.id
        res["context"] = action_context
        res["domain"] = (
            literal_eval(res["domain"]) + self._get_partner_contract_domain()
        )
        return res

    def _get_act_window_contract_xml(self, contract_type):
        if contract_type == "purchase":
            return self.env["ir.actions.act_window"]._for_xml_id(
                "contract.action_supplier_contract"
            )
        else:
            return self.env["ir.actions.act_window"]._for_xml_id(
                "contract.action_customer_contract"
            )
