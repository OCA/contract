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
    def _check_contact_is_not_terminated(self):
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
        """Create contracts for sale order lines that are contract products.

        Uses hooks _compute_contract_groups and _get_order_lines_for_group
        so that modules can extend the behavior without replacing the whole method.
        """
        contract_model = self.env["contract.contract"]
        contracts = []

        for rec in self.filtered("is_contract"):
            line_to_create_contract = rec.order_line.filtered(
                lambda r: not r.contract_id and r.product_id.is_contract
            )
            line_to_create_contract._set_contract_line_start_date()

            line_to_update_contract = rec.order_line.filtered(
                lambda r: r.contract_id
                and r.product_id.is_contract
                and r
                not in r.contract_id.contract_line_ids.mapped("sale_order_line_id")
            )
            contract_groups = self._compute_contract_groups(line_to_create_contract)

            for group in contract_groups:
                main_line, template = (
                    group if isinstance(group, tuple) else (None, group)
                )
                order_lines = self._get_order_lines_for_group(
                    line_to_create_contract, template, main_line
                )
                contract = contract_model.create(rec._prepare_contract_value(template))
                contracts.append(contract.id)
                contract._onchange_contract_template_id()
                order_lines.create_contract_line(contract)
                order_lines.write({"contract_id": contract.id})
            for line in line_to_update_contract:
                line.create_contract_line(line.contract_id)

        return contract_model.browse(contracts)

    def _compute_contract_groups(self, line_to_create_contract):
        """Compute contract templates or groups to create."""
        contract_templates = self.env["contract.template"]
        for order_line in line_to_create_contract:
            template = order_line.product_id.with_company(
                order_line.order_id.company_id
            ).property_contract_template_id
            if not template:
                raise ValidationError(
                    _(
                        "You must specify a contract "
                        "template for '{product_name}' product "
                        "in '{company_name}' company."
                    ).format(
                        product_name=order_line.product_id.name,
                        company_name=order_line.order_id.company_id.name,
                    )
                )
            contract_templates |= template
        return contract_templates

    def _get_order_lines_for_group(
        self, line_to_create_contract, template, main_line=None
    ):
        """Return the lines to include for a given template / group."""
        return line_to_create_contract.filtered(
            lambda r: r.product_id.with_company(
                r.order_id.company_id
            ).property_contract_template_id
            == template
        )

    def _get_filtered_children(self, line, template):
        """Return all child lines recursively that are contract products
        with the same contract template"""
        valid_children = line.child_ids.filtered(
            lambda sol: sol.product_id.is_contract
            and sol.product_id.property_contract_template_id == template
        )
        for child in valid_children:
            valid_children |= self._get_filtered_children(child, template)
        return valid_children

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
        action["domain"] = [("id", "in", contracts.ids)]
        if len(contracts) == 1:
            # If there is only one contract, open it directly
            action.update(
                {
                    "res_id": contracts.id,
                    "view_mode": "form",
                    "views": list(
                        filter(lambda view: view[1] == "form", action["views"])
                    ),
                }
            )
        return action
