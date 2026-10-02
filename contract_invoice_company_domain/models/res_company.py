# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    create_recurring_invoices = fields.Boolean(default=True)
    contract_to_invoice_domain = fields.Char(
        compute="_compute_contract_to_invoice_domain",
        store=True,
        readonly=False,
        help="Extra domain applied on the contracts of this company when the "
        "recurring invoices cron selects the contracts to invoice.",
    )

    @api.depends("create_recurring_invoices")
    def _compute_contract_to_invoice_domain(self):
        for company in self:
            # Drop the domain when recurring invoicing is off. Otherwise keep the
            # stored value: an unassigned stored computed field is reset to False
            # on recompute (see fields.py compute_value fallback).
            domain = company.contract_to_invoice_domain
            company.contract_to_invoice_domain = (
                domain if company.create_recurring_invoices else False
            )

    @api.constrains("contract_to_invoice_domain")
    def _check_contract_to_invoice_domain(self):
        for company in self:
            if not company.contract_to_invoice_domain:
                continue
            try:
                domain = literal_eval(company.contract_to_invoice_domain)
                self.env["contract.contract"]._where_calc(domain)
            except Exception as err:
                raise ValidationError(
                    self.env._(
                        "The contract invoicing domain is not valid: %s",
                        company.contract_to_invoice_domain,
                    )
                ) from err
