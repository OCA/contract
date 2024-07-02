# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_contract = fields.Boolean(string="Is a contract", compute="_compute_is_contract")
    contract_count = fields.Integer(compute="_compute_contract_count")
    need_contract_creation = fields.Boolean(compute="_compute_need_contract_creation")

    @api.constrains("state")
    def _check_contract_is_not_terminated(self):
        for rec in self:
            if rec.state not in (
                "sale",
                "done",
                "cancel",
            ) and rec.order_line.filtered("contract_id.is_terminated"):
                raise ValidationError(
                    _("You can't upsell or downsell a terminated contract")
                )

    @api.depends("order_line.contract_id", "state")
    def _compute_need_contract_creation(self):
        self.update({"need_contract_creation": False})
        for rec in self:
            if rec.state in ("sale", "done"):
                line_to_create_contract = rec.order_line.filtered(
                    lambda r: not r.contract_id and r.product_id.is_contract
                )
                line_to_update_contract = rec.order_line.filtered(
                    lambda r: r.contract_id
                    and r.product_id.is_contract
                    and r
                    not in r.contract_id.contract_line_ids.mapped("sale_order_line_id")
                )
                if line_to_create_contract or line_to_update_contract:
                    rec.need_contract_creation = True

    @api.depends("order_line")
    def _compute_is_contract(self):
        self.is_contract = any(self.order_line.mapped("is_contract"))

    def _prepare_contract_value(self, contract_template):
        self.ensure_one()
        return {
            "name": f"{contract_template.name}: {self.name}",
            "partner_id": self.partner_id.id,
            "company_id": self.company_id.id,
            "contract_template_id": contract_template.id,
            "user_id": self.user_id.id,
            "payment_term_id": self.payment_term_id.id,
            "fiscal_position_id": self.fiscal_position_id.id,
            "invoice_partner_id": self.partner_invoice_id.id,
            "line_recurrence": True,
        }

    def action_create_contract(self):
        contract_model = self.env["contract.contract"]
        contracts = []
        for rec in self.filtered("is_contract"):
            line_to_create_contract = rec.order_line.filtered(
                lambda r: not r.contract_id and r.product_id.is_contract
            )
            line_to_update_contract = rec.order_line.filtered(
                lambda r: r.contract_id
                and r.product_id.is_contract
                and r
                not in r.contract_id.contract_line_ids.mapped("sale_order_line_id")
            )
            contract_templates = self.env["contract.template"]
            for order_line in line_to_create_contract:
                contract_template = order_line.product_id.with_company(
                    rec.company_id
                ).property_contract_template_id
                if not contract_template:
                    raise ValidationError(
                        _(
                            "You must specify a contract "
                            "template for '%(product_name)s' product "
                            "in '%(company_name)s' company."
                        )
                        % {
                            "product_name": order_line.product_id.name,
                            "company_name": rec.company_id.name,
                        }
                    )
                contract_templates |= contract_template
            for contract_template in contract_templates:
                order_lines = line_to_create_contract.filtered(
                    lambda r, template=contract_template: r.product_id.with_company(
                        r.order_id.company_id
                    ).property_contract_template_id
                    == template
                )
                contract = contract_model.create(
                    rec._prepare_contract_value(contract_template)
                )
                contracts.append(contract.id)
                contract._onchange_contract_template_id()
                contract._onchange_contract_type()
                order_lines.create_contract_line(contract)
                order_lines.write({"contract_id": contract.id})
            for line in line_to_update_contract:
                line.create_contract_line(line.contract_id)
        return contract_model.browse(contracts)

    def action_confirm(self):
        """If we have a contract in the order, set it up"""
        self.filtered(
            lambda order: (order.company_id.create_contract_at_sale_order_confirmation)
        ).action_create_contract()
        return super().action_confirm()

    @api.depends("order_line")
    def _compute_contract_count(self):
        for rec in self:
            rec.contract_count = len(rec.order_line.mapped("contract_id"))

    def action_show_contracts(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "contract.action_customer_contract"
        )

        contracts = (
            self.env["contract.line"]
            .search([("sale_order_line_id", "in", self.order_line.ids)])
            .mapped("contract_id")
        )
        action["domain"] = [
            ("contract_line_ids.sale_order_line_id", "in", self.order_line.ids)
        ]
        if len(contracts) == 1:
            # If there is only one contract, open it directly
            action.update(
                {
                    "res_id": contracts.id,
                    "view_mode": "form",
                    "views": filter(lambda view: view[1] == "form", action["views"]),
                }
            )
        return action
