# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class AgreementSettlementCreateWiz(models.TransientModel):
    _name = "agreement.settlement.create.wiz"
    _description = "Agreement settlement create wizard"

    date = fields.Date(default=fields.Date.today)
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To", required=True)
    domain = fields.Selection("_domain_selection", default="sale")
    journal_ids = fields.Many2many(
        comodel_name="account.journal",
        string="Journals",
    )
    agreement_type_ids = fields.Many2many(
        comodel_name="agreement.type",
        string="Agreement types",
    )
    agreement_ids = fields.Many2many(
        comodel_name="agreement",
        string="Agreements",
    )
    discard_settled_agreement = fields.Boolean(
        string="Discard settled agreements",
        default="True",
        help="If checked, the agreements with settlements in selected period "
        "will be discard",
    )

    @api.model
    def _domain_selection(self):
        return self.env["agreement"]._domain_selection()

    def _prepare_agreement_domain(self):
        domain = [
            ("rebate_type", "!=", False),
            ("agreement_type_id.is_rebate", "=", True),
        ]
        settlement_domain = []
        if self.date_from:
            domain.extend(
                ["|", ("end_date", "=", False), ("end_date", ">=", self.date_from)]
            )
            settlement_domain.extend([("date_to", ">=", self.date_from)])
        if self.date_to:
            domain.extend([("start_date", "<=", self.date_to)])
            settlement_domain.extend([("date_to", "<=", self.date_to)])
        if self.agreement_ids:
            domain.extend([("id", "in", self.agreement_ids.ids)])
            settlement_domain.extend(
                [("line_ids.agreement_id", "in", self.agreement_ids.ids)]
            )
        elif self.agreement_type_ids:
            domain.extend([("agreement_type_id", "in", self.agreement_type_ids.ids)])
            settlement_domain.extend(
                [
                    (
                        "line_ids.agreement_id.agreement_type_id",
                        "in",
                        self.agreement_type_ids.ids,
                    )
                ]
            )
        else:
            domain.extend([("agreement_type_id.domain", "=", self.domain)])
        if self.discard_settled_agreement:
            settlements = self._get_existing_settlement(settlement_domain)
            if settlements:
                domain.extend(
                    [("id", "not in", settlements.mapped("line_ids.agreement_id").ids)]
                )
        return domain

    def _get_existing_settlement(self, domain):
        return self.env["agreement.rebate.settlement"].search(domain)

    def _get_target_model(self):
        return self.env["account.invoice.report"]

    def _prepare_target_domain(self):
        domain = [
            ("state", "not in", ["draft", "cancel"]),
        ]
        if self.journal_ids:
            domain.extend([("journal_id", "in", self.journal_ids.ids)])
        else:
            domain.extend([("journal_id.type", "=", self.domain)])
        if self.date_from:
            domain.extend(
                [
                    (
                        "invoice_date",
                        ">=",
                        fields.Date.to_string(self.date_from),
                    )
                ]
            )
        if self.date_to:
            domain.extend(
                [
                    (
                        "invoice_date",
                        "<=",
                        fields.Date.to_string(self.date_to),
                    )
                ]
            )
        return domain

    def _target_line_domain(self, agreement_domain, agreement, line=False):
        domain = agreement_domain.copy()
        if agreement.start_date:
            domain.append(
                (
                    "invoice_date",
                    ">=",
                    fields.Date.to_string(agreement.start_date),
                )
            )
        if agreement.end_date:
            domain.append(
                (
                    "invoice_date",
                    "<=",
                    fields.Date.to_string(agreement.end_date),
                )
            )
        if line:
            domain += safe_eval(line.rebate_domain)
        elif agreement.rebate_line_ids:
            domain = expression.AND(
                [
                    domain,
                    expression.OR(
                        [safe_eval(x.rebate_domain) for x in agreement.rebate_line_ids]
                    ),
                ]
            )
        return domain

    def get_agregate_fields(self):
        return [
            "price_subtotal",
        ]

    def _get_amount_field(self):
        return "price_subtotal"

    def _prepare_settlement_line(
        self, domain, group, agreement, line=False, section=False
    ):
        amount = group[self._get_amount_field()] or 0.0
        if self.domain == "purchase":
            amount = -amount
        amount += agreement.additional_consumption
        amount_section = 0.0
        vals = {
            "agreement_id": agreement.id,
            "partner_id": group["partner_id"][0]
            if "partner_id" in group
            else agreement.partner_id.id,
        }
        if agreement.rebate_type == "line":
            rebate = amount * line.rebate_discount / 100
            vals.update({"rebate_line_id": line.id, "percent": line.rebate_discount})
        elif agreement.rebate_type == "section_prorated":
            if amount >= section.amount_to:
                amount_section = section.amount_to
            elif amount >= section.amount_from:
                amount_section = amount - section.amount_from
            rebate = amount_section * section.rebate_discount / 100
            vals.update(
                {
                    "rebate_section_id": section.id,
                    "amount_from": section.amount_from,
                    "amount_to": section.amount_to,
                    "percent": section.rebate_discount,
                }
            )
        elif agreement.rebate_type == "global":
            rebate = amount * agreement.rebate_discount / 100
            vals.update({"percent": agreement.rebate_discount})
        elif agreement.rebate_type == "section_total":
            section = agreement.rebate_section_ids.filtered(
                lambda s: s.amount_from <= amount <= s.amount_to
            )
            rebate = amount * section.rebate_discount / 100
            vals.update(
                {
                    "percent": section.rebate_discount,
                    "amount_from": section.amount_from,
                    "amount_to": section.amount_to,
                }
            )
        vals.update(
            {
                "target_domain": domain,
                "amount_invoiced": agreement.company_id.currency_id.round(
                    amount_section or amount
                ),
                "amount_rebate": agreement.company_id.currency_id.round(rebate),
            }
        )
        return vals

    def _get_rebate_discount(self, agreement, amount):
        if agreement.rebate_type == "global":
            return agreement.rebate_discount
        if agreement.rebate_type == "section_total":
            section = agreement.rebate_section_ids.filtered(
                lambda s: s.amount_from <= amount <= s.amount_to
            )
            return section.rebate_discount

    def _partner_domain(self, agreement):
        return [
            ("partner_id", "child_of", agreement.partner_id.ids),
        ]

    def get_settlement_key(self, agreement):
        return agreement

    def action_create_settlement(self):
        self.ensure_one()
        Agreement = self.env["agreement"]
        target_model = self._get_target_model()
        orig_domain = self._prepare_target_domain()
        settlement_dic = defaultdict(lambda: {"lines": []})
        agreements = Agreement.search(self._prepare_agreement_domain())
        for agreement in agreements:
            key = self.get_settlement_key(agreement)
            if key not in settlement_dic:
                settlement_dic[key]["amount_rebate"] = 0.0
                settlement_dic[key]["amount_invoiced"] = 0.0
                settlement_dic[key]["partner_id"] = agreement.partner_id.id
            agreement_domain = orig_domain + self._partner_domain(agreement)
            if agreement.rebate_type == "line":
                if not agreement.rebate_line_ids:
                    continue
                for line in agreement.rebate_line_ids:
                    domain = self._target_line_domain(
                        agreement_domain, agreement, line=line
                    )
                    groups = target_model.read_group(
                        domain,
                        self.get_agregate_fields(),
                        self._settlement_line_break_fields(),
                        lazy=False,
                    )
                    if (
                        not groups
                        or not groups[0]["__count"]
                        and not agreement.additional_consumption
                    ):
                        continue
                    for group in groups:
                        vals = self._prepare_settlement_line(
                            domain, group, agreement, line=line
                        )
                        settlement_dic[key]["amount_rebate"] += vals["amount_rebate"]
                        settlement_dic[key]["amount_invoiced"] += vals[
                            "amount_invoiced"
                        ]
                        settlement_dic[key]["lines"].append((0, 0, vals))
            elif agreement.rebate_type == "section_prorated":
                domain = self._target_line_domain(agreement_domain, agreement)
                groups = target_model.read_group(
                    domain,
                    self.get_agregate_fields(),
                    self._settlement_line_break_fields(),
                    lazy=False,
                )
                if (
                    not groups
                    or not groups[0]["__count"]
                    and not agreement.additional_consumption
                ):
                    continue
                amount = groups and groups[0][self._get_amount_field()] or 0.0
                for section in agreement.rebate_section_ids:
                    if amount < section.amount_to and amount < section.amount_from:
                        break
                    for group in groups:
                        vals = self._prepare_settlement_line(
                            domain, group, agreement, section=section
                        )
                        settlement_dic[key]["amount_rebate"] += vals["amount_rebate"]
                        settlement_dic[key]["lines"].append((0, 0, vals))
                settlement_dic[key]["amount_invoiced"] += amount
            else:
                domain = self._target_line_domain(agreement_domain, agreement)
                groups = target_model.read_group(
                    domain,
                    self.get_agregate_fields(),
                    self._settlement_line_break_fields(),
                    lazy=False,
                )
                if (
                    not groups
                    or not groups[0]["__count"]
                    and not agreement.additional_consumption
                ):
                    continue
                for group in groups:
                    vals = self._prepare_settlement_line(domain, group, agreement)
                    settlement_dic[key]["lines"].append((0, 0, vals))
                    settlement_dic[key]["amount_rebate"] += vals["amount_rebate"]
                    settlement_dic[key]["amount_invoiced"] += vals["amount_invoiced"]
        settlements = self._create_settlement(settlement_dic)
        return settlements.action_show_settlement()

    def _settlement_line_break_fields(self):
        return ["partner_id"]

    def _filter_settlement_lines(self, settlement_lines):
        return [
            line
            for line in filter(lambda l: l[2]["amount_rebate"] != 0.0, settlement_lines)
        ]

    def _prepare_settlement(self, settlement_lines):
        lines = self._filter_settlement_lines(settlement_lines["lines"])
        if not lines:
            return {}
        return {
            "date": self.date,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "line_ids": lines,
            "partner_id": settlement_lines["partner_id"],
            "amount_rebate": settlement_lines["amount_rebate"],
            "amount_invoiced": settlement_lines["amount_invoiced"],
        }

    def _create_settlement(self, settlements):
        vals_list = []
        for settlement_lines in settlements.values():
            vals = self._prepare_settlement(settlement_lines)
            if vals:
                vals_list.append(vals)
        return self.env["agreement.rebate.settlement"].create(vals_list)
