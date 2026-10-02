# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo import api, models
from odoo.osv import expression


class ContractContract(models.Model):
    _inherit = "contract.contract"

    @api.model
    def _get_contracts_to_invoice_domain(self, date_ref=None):
        domain = super()._get_contracts_to_invoice_domain(date_ref=date_ref)
        company_clauses = []
        for company in self.env["res.company"].sudo().search([]):
            if not company.create_recurring_invoices:
                # This company must never generate recurring invoices.
                company_clauses.append([("company_id", "!=", company.id)])
                continue
            if not company.contract_to_invoice_domain:
                continue
            extra_domain = literal_eval(company.contract_to_invoice_domain)
            if extra_domain:
                # The extra domain restricts this company's contracts only.
                company_clauses.append(
                    expression.OR([[("company_id", "!=", company.id)], extra_domain])
                )
        if company_clauses:
            domain = expression.AND([domain] + company_clauses)
        return domain
