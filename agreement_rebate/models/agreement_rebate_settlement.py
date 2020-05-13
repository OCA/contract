# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import safe_eval


class AgreementRebateSettlement(models.Model):
    _name = "agreement.rebate.settlement"
    _description = "Agreement Rebate Settlement"
    _order = "date DESC"

    name = fields.Char(required=True, default="/")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    date = fields.Date(default=fields.Date.today)
    date_from = fields.Date()
    date_to = fields.Date()
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner",)
    line_ids = fields.One2many(
        comodel_name="agreement.rebate.settlement.line",
        inverse_name="settlement_id",
        string="Settlement Lines",
    )
    amount_invoiced = fields.Float(string="Amount invoiced")
    amount_rebate = fields.Float(string="Amount rebate")
    invoice_id = fields.Many2one(comodel_name="account.move", string="Invoice")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") != "/":
                continue
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "agreement.rebate.settlement"
            )
        return super(AgreementRebateSettlement, self).create(vals_list)

    def _reverse_type_map(self, inv_type):
        return {
            "out_invoice": "out_refund",
            "out_refund": "out_invoice",
            "in_invoice": "in_refund",
            "in_refund": "in_invoice",
        }.get(inv_type)

    def create_invoice(self):
        invoice_dic = {}
        for line in self.mapped("line_ids"):
            key = line._get_invoice_key()
            if key not in invoice_dic:
                invoice_dic[key] = line._prepare_invoice()
                invoice_dic[key]["processed_settlements"] = line.settlement_id
                invoice_dic[key]["check_amount"] = 0.0
            elif line.settlement_id not in invoice_dic[key]["processed_settlements"]:
                invoice_dic[key]["invoice_origin"] = "{}, {}".format(
                    invoice_dic[key]["invoice_origin"], line.settlement_id.name
                )
                invoice_dic[key]["processed_settlements"] |= line.settlement_id
            inv_line_vals = line._prepare_invoice_line(invoice_dic[key])
            invoice_dic[key]["invoice_line_ids"].append((0, 0, inv_line_vals))
            invoice_dic[key]["check_amount"] += line.amount_invoiced
        for values in invoice_dic.values():
            values.pop("processed_settlements", None)
            values.pop("line_ids", None)
            if values.pop("check_amount", 0.0) < 0.0:
                for line_vals in values["invoice_line_ids"]:
                    line_vals[2]["price_unit"] *= -1
                values["type"] = self._reverse_type_map(values["type"])
        invoices = self.env["account.move"].create(invoice_dic.values())
        return invoices

    def action_show_detail(self):
        target_domains = self.line_ids.mapped("target_domain")
        domain = expression.OR([safe_eval(d) for d in set(target_domains)])
        return {
            "name": _("Details"),
            "type": "ir.actions.act_window",
            "res_model": "account.invoice.report",
            "view_mode": "pivot,tree",
            "domain": domain,
            "context": self.env.context,
        }

    def action_show_settlement(self):
        action = self.env.ref(
            "agreement_rebate.agreement_rebate_settlement_action"
        ).read()[0]
        if len(self) == 1:
            form = self.env.ref("agreement_rebate.agreement_rebate_settlement_form")
            action["views"] = [(form.id, "form")]
            action["res_id"] = self.id
        else:
            action["domain"] = [("id", "in", self.ids)]
        return action

    def action_show_agreement(self):
        agreements = self.line_ids.mapped("agreement_id")
        action = self.env.ref("agreement.agreement_action").read()[0]
        if len(agreements) == 1:
            form = self.env.ref("agreement.agreement_form")
            action["views"] = [(form.id, "form")]
            action["res_id"] = agreements.id
        else:
            action["domain"] = [("id", "in", agreements.ids)]
        return action


class AgreementRebateSettlementLine(models.Model):
    _name = "agreement.rebate.settlement.line"
    _description = "Agreement Rebate Settlement Lines"
    _order = "date DESC"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        related="settlement_id.company_id",
    )
    settlement_id = fields.Many2one(
        comodel_name="agreement.rebate.settlement",
        string="Rebate settlement",
        ondelete="cascade",
    )
    date = fields.Date(related="settlement_id.date", store=True,)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner",)
    rebate_line_id = fields.Many2one(
        comodel_name="agreement.rebate.line", string="Rebate Line",
    )
    rebate_section_id = fields.Many2one(
        comodel_name="agreement.rebate.section", string="Rebate section",
    )
    target_domain = fields.Char()
    amount_from = fields.Float(string="From", readonly=True)
    amount_to = fields.Float(string="To", readonly=True)
    percent = fields.Float(string="Percent", readonly=True)
    amount_gross = fields.Float(string="Amount gross")
    amount_invoiced = fields.Float(string="Amount invoiced")
    amount_rebate = fields.Float(string="Amount rebate")
    agreement_id = fields.Many2one(
        comodel_name="agreement", string="Agreement", required=True,
    )
    rebate_type = fields.Selection(
        related="agreement_id.rebate_type", string="Rebate type",
    )
    invoice_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        relation="agreement_rebate_settlement_line_account_invoice_line_rel",
        column1="settlement_line_id",
        column2="invoice_line_id",
        string="Invoice lines",
    )
    invoice_status = fields.Selection(
        [
            ("invoiced", "Fully Invoiced"),
            ("to_invoice", "To Invoice"),
            ("no", "Nothing to Invoice"),
        ],
        string="Invoice Status",
        compute="_compute_invoice_status",
        store=True,
        readonly=False,
    )

    @api.depends(
        "invoice_line_ids",
        "invoice_line_ids.parent_state",
        "invoice_line_ids.refund_line_ids",
    )
    def _compute_invoice_status(self):
        for line in self:
            if line.invoice_status == "no":
                continue
            invoice_lines = line.invoice_line_ids.filtered(
                lambda ln: ln.parent_state != "cancel"
            )
            refund_lines = invoice_lines.refund_line_ids.filtered(
                lambda ln: ln.parent_state != "cancel"
            )
            if invoice_lines and not refund_lines:
                line.invoice_status = "invoiced"
            else:
                line.invoice_status = "to_invoice"

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order.
        This method may be overridden to implement custom invoice generation
        (making sure to call super() to establish a clean extension chain).
        """
        self.ensure_one()
        company_id = self.company_id.id or self.env.user.company_id.id
        partner = self.env.context.get("partner_invoice", False)
        if not partner:
            invoice_group = self.env.context.get("invoice_group", "settlement")
            if invoice_group == "settlement":
                partner = self.settlement_id.partner_id
            elif invoice_group == "partner":
                partner = self.partner_id
            elif invoice_group == "commercial_partner":
                partner = self.partner_id.commercial_partner_id
        invoice_type = self.env.context.get("invoice_type", "out_invoice")
        journal_id = (
            self.env.context.get("journal_id")
            or self.env["account.move"]
            .with_context(force_company=company_id)
            .default_get(["journal_id"])["journal_id"]
        )
        if not journal_id:
            raise UserError(
                _("Please define an accounting sales journal for" " this company.")
            )
        vinvoice = self.env["account.move"].new(
            {
                "company_id": company_id,
                "partner_id": partner.id,
                "type": invoice_type,
                "journal_id": journal_id,
            }
        )
        # Get partner extra fields
        vinvoice._onchange_partner_id()
        invoice_vals = vinvoice._convert_to_write(vinvoice._cache)
        invoice_vals.update(
            {
                "ref": (self.agreement_id.name or ""),
                "invoice_origin": self.settlement_id.name,
                "invoice_line_ids": [],
                "currency_id": partner.currency_id.id,
                # 'comment': self.note,
                # 'user_id': self.user_id and self.user_id.id,
                # 'team_id': self.team_id.id,
            }
        )
        return invoice_vals

    def _prepare_invoice_line(self, invoice_vals):
        self.ensure_one()
        company_id = self.company_id.id or self.env.user.company_id.id
        product = self.env.context.get("product", False)
        invoice_line_vals = {
            "product_id": product.id,
            "quantity": 1.0,
            "product_uom_id": product.uom_id.id,
            "agreement_rebate_settlement_line_ids": [(4, self.id)],
        }
        invoice_line = (
            self.env["account.move.line"]
            .with_context(force_company=company_id,)
            .new(invoice_line_vals)
        )
        invoice_vals_new = invoice_vals.copy()
        invoice_vals_new.pop("processed_settlements", None)
        invoice_vals_new.pop("check_amount", None)
        invoice = (
            self.env["account.move"]
            .with_context(force_company=company_id,)
            .new(invoice_vals_new)
        )
        invoice_line.move_id = invoice
        # Get other invoice line values from product onchange
        invoice_line._onchange_product_id()
        invoice_line_vals = invoice_line._convert_to_write(invoice_line._cache)
        invoice_line_vals.update(
            {
                "name": _(
                    "{} - Period: {} - {}".format(
                        invoice_line_vals["name"],
                        self.settlement_id.date_from,
                        self.settlement_id.date_to,
                    )
                ),
                # 'account_analytic_id': self.analytic_account_id.id,
                # 'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
                "price_unit": self.amount_rebate,
            }
        )
        return invoice_line_vals

    def _get_invoice_key(self):
        invoice_group = self.env.context.get("invoice_group", "settlement")
        if invoice_group == "settlement":
            return self.settlement_id.id
        if invoice_group == "partner":
            return self.env.context.get("partner_id", self.partner_id.id)
        if invoice_group == "commercial_partner":
            return self.env.context.get(
                "partner_id", self.partner_id.commercial_partner_id.id
            )

    def action_show_detail(self):
        return {
            "name": _("Details"),
            "type": "ir.actions.act_window",
            "res_model": "account.invoice.report",
            "view_mode": "pivot,tree",
            "domain": self.target_domain,
            "context": self.env.context,
        }
