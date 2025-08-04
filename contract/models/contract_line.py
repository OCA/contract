# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import warnings

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ContractLine(models.Model):
    _name = "contract.line"
    _description = "Contract Line"
    _inherit = [
        "contract.template.line",
        "analytic.mixin",
    ]
    _order = "sequence,id"

    sequence = fields.Integer()
    contract_id = fields.Many2one(
        comodel_name="contract.contract",
        string="Contract",
        required=True,
        index=True,
        auto_join=True,
        ondelete="cascade",
    )
    currency_id = fields.Many2one(related="contract_id.currency_id")
    create_invoice_visibility = fields.Boolean(
        compute="_compute_create_invoice_visibility"
    )
    active = fields.Boolean(
        string="Active",
        related="contract_id.active",
        store=True,
        readonly=True,
    )
    product_id = fields.Many2one(index=True)

    @api.depends("name", "date_start")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.date_start} - {rec.name}"

    @api.model
    def _compute_first_recurring_next_date(
        self,
        date_start,
        recurring_invoicing_type,
        recurring_rule_type,
        recurring_interval,
    ):
        # deprecated method for backward compatibility
        return self.get_next_invoice_date(
            date_start,
            recurring_invoicing_type,
            self._get_default_recurring_invoicing_offset(
                recurring_invoicing_type, recurring_rule_type
            ),
            recurring_rule_type,
            recurring_interval,
            max_date_end=False,
        )

    @api.constrains("recurring_next_date", "date_start")
    def _check_recurring_next_date_start_date(self):
        for line in self:
            if line.display_type == "line_section" or not line.recurring_next_date:
                continue
            if line.date_start and line.recurring_next_date:
                if line.date_start > line.recurring_next_date:
                    raise ValidationError(
                        self.env._(
                            "You can't have a date of next invoice anterior "
                            "to the start of the contract line '%s'"
                        )
                        % line.name
                    )

    @api.constrains(
        "date_start", "date_end", "last_date_invoiced", "recurring_next_date"
    )
    def _check_last_date_invoiced(self):
        for rec in self.filtered("last_date_invoiced"):
            if rec.date_end and rec.date_end < rec.last_date_invoiced:
                raise ValidationError(
                    self.env._(
                        "You can't have the end date before the date of last "
                        "invoice for the contract line '%s'"
                    )
                    % rec.name
                )
            if not rec.contract_id.line_recurrence:
                continue
            if rec.date_start and rec.date_start > rec.last_date_invoiced:
                raise ValidationError(
                    self.env._(
                        "You can't have the start date after the date of last "
                        "invoice for the contract line '%s'"
                    )
                    % rec.name
                )
            if (
                rec.recurring_next_date
                and rec.recurring_next_date <= rec.last_date_invoiced
            ):
                raise ValidationError(
                    self.env._(
                        "You can't have the next invoice date before the date "
                        "of last invoice for the contract line '%s'"
                    )
                    % rec.name
                )

    @api.constrains("recurring_next_date")
    def _check_recurring_next_date_recurring_invoices(self):
        for rec in self:
            if not rec.recurring_next_date and (
                not rec.date_end
                or not rec.last_date_invoiced
                or rec.last_date_invoiced < rec.date_end
            ):
                raise ValidationError(
                    self.env._(
                        "You must supply a date of next invoice for contract "
                        "line '%s'"
                    )
                    % rec.name
                )

    @api.constrains("date_start", "date_end")
    def _check_start_end_dates(self):
        for line in self.filtered("date_end"):
            if line.date_start and line.date_end:
                if line.date_start > line.date_end:
                    raise ValidationError(
                        self.env._(
                            "Contract line '%s' start date can't be later than"
                            " end date"
                        )
                        % line.name
                    )

    @api.depends(
        "display_type",
        "is_recurring_note",
        "recurring_next_date",
        "date_start",
        "date_end",
    )
    def _compute_create_invoice_visibility(self):
        # TODO: depending on the lines, and their order, some sections
        # have no meaning in certain invoices
        today = fields.Date.context_today(self)
        for rec in self:
            if (
                (not rec.display_type or rec.is_recurring_note)
                and rec.date_start
                and today >= rec.date_start
            ):
                rec.create_invoice_visibility = bool(rec.recurring_next_date)
            else:
                rec.create_invoice_visibility = False

    def _prepare_invoice_line(self):
        self.ensure_one()
        dates = self._get_period_to_invoice(
            self.last_date_invoiced, self.recurring_next_date
        )
        name = self._insert_markers(dates[0], dates[1])
        return {
            "quantity": self._get_quantity_to_invoice(*dates),
            "product_uom_id": self.uom_id.id,
            "discount": self.discount,
            "contract_line_id": self.id,
            "analytic_distribution": self.analytic_distribution,
            "sequence": self.sequence,
            "name": name,
            "price_unit": self.price_unit,
            "display_type": self.display_type or "product",
            "product_id": self.product_id.id,
        }

    def _get_period_to_invoice(
        self, last_date_invoiced, recurring_next_date, stop_at_date_end=True
    ):
        # TODO this method can now be removed, since
        # TODO self.next_period_date_start/end have the same values
        self.ensure_one()
        if not recurring_next_date:
            return False, False, False
        first_date_invoiced = (
            last_date_invoiced + relativedelta(days=1)
            if last_date_invoiced
            else self.date_start
        )
        last_date_invoiced = self.get_next_period_date_end(
            first_date_invoiced,
            self.recurring_rule_type,
            self.recurring_interval,
            max_date_end=(self.date_end if stop_at_date_end else False),
            next_invoice_date=recurring_next_date,
            recurring_invoicing_type=self.recurring_invoicing_type,
            recurring_invoicing_offset=self.recurring_invoicing_offset,
        )
        return first_date_invoiced, last_date_invoiced, recurring_next_date

    def _translate_marker_month_name(self, month_name):
        months = {
            "01": self.env._("January"),
            "02": self.env._("February"),
            "03": self.env._("March"),
            "04": self.env._("April"),
            "05": self.env._("May"),
            "06": self.env._("June"),
            "07": self.env._("July"),
            "08": self.env._("August"),
            "09": self.env._("September"),
            "10": self.env._("October"),
            "11": self.env._("November"),
            "12": self.env._("December"),
        }
        return months[month_name]

    def _insert_markers(self, first_date_invoiced, last_date_invoiced):
        self.ensure_one()
        lang_obj = self.env["res.lang"]
        lang = lang_obj.search([("code", "=", self.contract_id.partner_id.lang)])
        date_format = lang.date_format or "%m/%d/%Y"
        name = self.name
        name = name.replace("#START#", first_date_invoiced.strftime(date_format))
        name = name.replace("#END#", last_date_invoiced.strftime(date_format))
        name = name.replace(
            "#INVOICEMONTHNAME#",
            self.with_context(lang=lang.code)._translate_marker_month_name(
                first_date_invoiced.strftime("%m")
            ),
        )
        return name

    def _update_recurring_next_date(self):
        warnings.warn(
            "Deprecated _update_recurring_next_date, "
            "use _update_last_date_invoiced instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._update_last_date_invoiced()

    def _update_last_date_invoiced(self):
        for rec in self:
            last_date_invoiced = rec.next_period_date_end
            rec.write(
                {
                    "last_date_invoiced": last_date_invoiced,
                }
            )

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        default_contract_type = self.env.context.get("default_contract_type")
        if view_type == "list" and default_contract_type == "purchase":
            view_id = self.env.ref("contract.contract_line_supplier_tree_view").id
        if view_type == "form":
            if default_contract_type == "purchase":
                view_id = self.env.ref("contract.contract_line_supplier_form_view").id
            elif default_contract_type == "sale":
                view_id = self.env.ref("contract.contract_line_customer_form_view").id
        return super().get_view(view_id, view_type, **options)

    def _get_quantity_to_invoice(
        self, period_first_date, period_last_date, invoice_date
    ):
        self.ensure_one()
        return self.quantity if not self.display_type else 0.0
