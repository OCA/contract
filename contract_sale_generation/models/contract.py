# © 2004-2010 OpenERP SA
# © 2014 Angel Moya <angel.moya@domatix.com>
# © 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# Copyright 2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    sale_count = fields.Integer(compute="_compute_sale_count")

    def _prepare_sale(self, date_ref):
        self.ensure_one()
        sale = self.env["sale.order"].new(
            {
                "partner_id": self.partner_id,
                "date_order": fields.Date.to_string(date_ref),
                "origin": self.name,
                "company_id": self.company_id.id,
                "user_id": self.partner_id.user_id.id,
                "analytic_account_id": self.group_id.id,
            }
        )
        if self.payment_term_id:
            sale.payment_term_id = self.payment_term_id.id
        if self.fiscal_position_id:
            sale.fiscal_position_id = self.fiscal_position_id.id
        # Get other sale values from partner onchange
        sale.onchange_partner_id()
        return sale._convert_to_write(sale._cache)

    def _get_related_sales(self):
        self.ensure_one()
        sales = (
            self.env["sale.order.line"]
            .search([("contract_line_id", "in", self.contract_line_ids.ids)])
            .mapped("order_id")
        )
        return sales

    def _compute_sale_count(self):
        for rec in self:
            rec.sale_count = len(rec._get_related_sales())

    def action_show_sales(self):
        self.ensure_one()
        tree_view = self.env.ref("sale.view_order_tree", raise_if_not_found=False)
        form_view = self.env.ref("sale.view_order_form", raise_if_not_found=False)
        action = {
            "type": "ir.actions.act_window",
            "name": "Sales Orders",
            "res_model": "sale.order",
            "view_type": "form",
            "view_mode": "tree,kanban,form,calendar,pivot,graph,activity",
            "domain": [("id", "in", self._get_related_sales().ids)],
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action

    def recurring_create_sale(self):
        """
        This method triggers the creation of the next sale order of the
        contracts even if their next sale order date is in the future.
        """
        sales = self._recurring_create_sale()
        for sale_rec in sales:
            self.message_post(
                body=_(
                    "Contract manually sale order: "
                    '<a href="#" data-oe-model="%s" data-oe-id="%s">'
                    "Sale Order"
                    "</a>"
                )
                % (sale_rec._name, sale_rec.id)
            )
        return sales

    def _prepare_recurring_sales_values(self, date_ref=False):
        """
        This method builds the list of sales values to create, based on
        the lines to sale of the contracts in self.
        !!! The date of next invoice (recurring_next_date) is updated here !!!
        :return: list of dictionaries (invoices values)
        """
        sales_values = []
        for contract in self:
            if not date_ref:
                date_ref = contract.recurring_next_date
            if not date_ref:
                # this use case is possible when recurring_create_invoice is
                # called for a finished contract
                continue
            contract_lines = contract._get_lines_to_invoice(date_ref)
            if not contract_lines:
                continue
            sale_values = contract._prepare_sale(date_ref)
            for line in contract_lines:
                sale_values.setdefault("order_line", [])
                invoice_line_values = line._prepare_sale_line(
                    sale_values=sale_values,
                )
                if invoice_line_values:
                    sale_values["order_line"].append((0, 0, invoice_line_values))
            sales_values.append(sale_values)
            contract_lines._update_recurring_next_date()
        return sales_values

    def _recurring_create_sale(self, date_ref=False):
        sales_values = self._prepare_recurring_sales_values(date_ref)
        sale_orders = self.env["sale.order"].create(sales_values)
        sale_orders_to_confirm = sale_orders.filtered(
            lambda sale: sale.contract_auto_confirm
        )
        sale_orders_to_confirm.action_confirm()
        return sale_orders

    @api.model
    def _get_recurring_create_func(self, create_type="invoice"):
        res = super()._get_recurring_create_func(create_type=create_type)
        if create_type == "sale":
            return self.__class__._recurring_create_sale
        return res

    @api.model
    def cron_recurring_create_sale(self, date_ref=None):
        return self._cron_recurring_create(date_ref, create_type="sale")
