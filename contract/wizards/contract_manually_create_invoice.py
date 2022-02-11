# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import (
    AccessDenied,
    AccessError,
    MissingError,
    UserError,
    ValidationError,
)


class ContractManuallyCreateInvoice(models.TransientModel):

    _name = "contract.manually.create.invoice"
    _description = "Contract Manually Create Invoice Wizard"

    invoice_date = fields.Date(required=True)
    contract_to_invoice_count = fields.Integer(
        compute="_compute_contract_to_invoice_ids"
    )
    contract_to_invoice_ids = fields.Many2many(
        comodel_name="contract.contract",
        compute="_compute_contract_to_invoice_ids",
    )
    contract_type = fields.Selection(
        selection=[("sale", "Customer"), ("purchase", "Supplier")],
        default="sale",
        required=True,
    )

    @api.depends("invoice_date")
    def _compute_contract_to_invoice_ids(self):
        if not self.invoice_date:
            # trick to show no invoice when no date has been entered yet
            contract_to_invoice_domain = [("id", "=", False)]
        else:
            contract_to_invoice_domain = self.env[
                "contract.contract"
            ]._get_contracts_to_invoice_domain(self.invoice_date)
        self.contract_to_invoice_ids = self.env["contract.contract"].search(
            contract_to_invoice_domain + [("contract_type", "=", self.contract_type)]
        )
        self.contract_to_invoice_count = len(self.contract_to_invoice_ids)

    def action_show_contract_to_invoice(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Contracts to invoice"),
            "res_model": "contract.contract",
            "domain": [("id", "in", self.contract_to_invoice_ids.ids)],
            "view_mode": "tree,form",
            "context": self.env.context,
        }

    def create_invoice(self):
        self.ensure_one()
        invoices = self.env["account.move"]
        for contract in self.contract_to_invoice_ids:
            try:
                invoices |= contract.recurring_create_invoice()
            except (
                AccessDenied,
                AccessError,
                MissingError,
                UserError,
                ValidationError,
            ) as oe:
                raise UserError(
                    _(
                        "Failed to process the contract %(name)s [id: %(id)s]:\n%(ue)s",
                        name=contract.name,
                        id=contract.id,
                        ue=repr(oe),
                    )
                ) from oe

        return {
            "type": "ir.actions.act_window",
            "name": _("Invoices"),
            "res_model": "account.move",
            "domain": [("id", "in", invoices.ids)],
            "view_mode": "tree,form",
            "context": self.env.context,
        }
