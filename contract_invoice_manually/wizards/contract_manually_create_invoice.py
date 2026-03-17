# Copyright 2026 ACSONE SA/NV
# Copyright 2026 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class ContractManuallyCreateInvoice(models.TransientModel):
    _inherit = "contract.manually.create.invoice"

    manually_invoiced = fields.Boolean(
        default=lambda self: self.env.company.enable_contract_invoice_manually
    )

    filter_domain = fields.Char(
        string="Domain",
        compute="_compute_filter_domain",
        store=True,
        readonly=False,
        help="Filter/Domain to apply on contracts to invoice",
    )

    @api.depends("invoice_date", "contract_type", "manually_invoiced")
    def _compute_filter_domain(self):
        for wizard in self:
            domain = [
                (
                    "recurring_next_date",
                    "<=",
                    fields.Datetime.to_string(wizard.invoice_date),
                ),
                ("contract_type", "=", wizard.contract_type),
                ("is_manually_invoiced", "=", wizard.manually_invoiced),
            ]
            wizard.filter_domain = str(domain)

    @api.depends("invoice_date", "filter_domain")
    def _compute_contract_to_invoice_ids(self):
        """
        Overwrite domain
        """
        super()._compute_contract_to_invoice_ids()
        Contract = self.env["contract.contract"]
        for wizard in self:
            contracts = Contract.search(safe_eval(wizard.filter_domain))
            wizard.contract_to_invoice_ids = contracts
            wizard.contract_to_invoice_count = len(contracts)
        return
