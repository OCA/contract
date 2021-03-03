# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from ast import literal_eval

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CreateContractWizard(models.TransientModel):
    _name = "create.contract.wizard"
    _description = "Create Contract Wizard"

    contract_type = fields.Selection(
        selection=[("sale", "Customer"), ("purchase", "Supplier")],
        default="sale",
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company.id,
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal",
        domain="[('type', '=', contract_type), ('company_id', '=', company_id)]",
        compute="_compute_journal_id",
        store=True,
        readonly=False,
        required=True,
    )
    recurring_interval = fields.Integer(
        default=1,
        string="Invoice Every",
        required=True,
        help="Invoice every (Days/Week/Month/Year)",
    )
    recurring_rule_type = fields.Selection(
        selection=[
            ("daily", "Day(s)"),
            ("weekly", "Week(s)"),
            ("monthly", "Month(s)"),
            ("monthlylastday", "Month(s) last day"),
            ("quarterly", "Quarter(s)"),
            ("semesterly", "Semester(s)"),
            ("yearly", "Year(s)"),
        ],
        default="monthly",
        string="Recurrence",
        required=True,
        help="Specify Interval for automatic invoice generation.",
    )
    recurring_invoicing_type = fields.Selection(
        selection=[("pre-paid", "Pre-paid"), ("post-paid", "Post-paid")],
        default="pre-paid",
        string="Invoicing type",
        required=True,
        help=(
            "Specify if the invoice must be generated at the beginning "
            "(pre-paid) or end (post-paid) of the period."
        ),
    )
    date_start = fields.Date(
        string="Date Start",
        required=True,
    )
    date_end = fields.Date(
        string="Date End",
        required=True,
    )

    @api.depends("contract_type", "company_id")
    def _compute_journal_id(self):
        AccountJournal = self.env["account.journal"]
        for rec in self:
            domain = [
                ("type", "=", rec.contract_type),
                ("company_id", "=", rec.company_id.id),
            ]
            journal = AccountJournal.search(domain, limit=1)
            if journal:
                rec.journal_id = journal.id

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        agreements = self.env["agreement"].browse(self._context.get("active_ids", []))
        if len(agreements) == 1:
            res["date_start"] = agreements[0].start_date
            res["date_end"] = agreements[0].end_date
        return res

    @api.model
    def view_init(self, fields):
        active_model = self._context.get("active_model")
        active_id = self._context.get("active_id")
        if active_model == "agreement":
            agreement = self.env[active_model].browse(active_id)
            contracts = self.env["contract.contract"].search(
                [("agreement_id", "=", active_id)]
            )
            if contracts:
                raise UserError(
                    _(
                        "Contract is created already, "
                        "please archive all before new create."
                    )
                )
            if not agreement.line_ids:
                raise UserError(_("No agreement lines !!"))
        return super().view_init(fields)

    def write_agreement(self, agreement):
        agreement.write(
            {
                "contract_type": self.contract_type,
            }
        )
        return agreement

    def prepare_contract(self, agreement):
        contract = self.env["contract.contract"].new(
            {
                "name": agreement.name,
                "partner_id": agreement.partner_id.id,
                "agreement_id": agreement.id,
                "contract_type": self.contract_type,
                "journal_id": self.journal_id.id,
                "recurring_interval": self.recurring_interval,
                "recurring_rule_type": self.recurring_rule_type,
                "recurring_invoicing_type": self.recurring_invoicing_type,
                "date_start": self.date_start,
                "date_end": self.date_end,
                "company_id": self.company_id.id,
            }
        )
        contract._onchange_partner_id()
        contract._onchange_contract_type()
        vals = contract._convert_to_write(contract._cache)
        return vals

    def prepare_contract_line(self, line, contract):
        date = contract.recurring_next_date or fields.Date.context_today(self)
        partner = contract.partner_id or self.env.user.partner_id
        price_unit = line.product_id.with_context(
            lang=partner.lang,
            partner=partner.id,
            quantity=line.qty,
            date=date,
            pricelist=contract.pricelist_id.id,
            uom=line.uom_id.id,
        ).price
        contract_line = self.env["contract.line"].new(
            {
                "product_id": line.product_id.id,
                "name": line.name,
                "quantity": line.qty,
                "price_unit": price_unit,
                "uom_id": line.uom_id.id,
                "recurring_interval": contract.recurring_interval,
                "recurring_rule_type": contract.recurring_rule_type,
                "recurring_invoicing_type": contract.recurring_invoicing_type,
                "date_start": contract.date_start,
                "date_end": contract.date_end,
                "recurring_next_date": contract.recurring_next_date,
            }
        )
        contract_line._inverse_price_unit()
        vals = contract_line._convert_to_write(contract_line._cache)
        return vals

    def create_contract(self):
        self.ensure_one()
        agreements = self.env["agreement"].browse(self._context.get("active_ids", []))
        contracts = self.env["contract.contract"]
        for agreement in agreements:
            vals = self.prepare_contract(agreement)
            contract = self.env["contract.contract"].create(vals)
            contract_line_ids = []
            for line in agreement.line_ids:
                line_vals = self.prepare_contract_line(line, contract)
                contract_line_ids += [(0, 0, line_vals)]
            if contract_line_ids:
                contract.write(
                    {
                        "contract_line_ids": contract_line_ids,
                    }
                )
            contracts |= contract
            self.write_agreement(agreement)
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
                "domain": [("id", "in", contracts.ids)],
                "context": context,
            }
        )
        return action
