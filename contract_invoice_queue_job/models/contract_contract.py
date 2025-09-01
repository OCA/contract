# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, tools

from .res_config_settings import CONTRACT_INVOICING_CHUNK_SIZE


class ContractContract(models.Model):
    _inherit = "contract.contract"

    @api.model
    def cron_recurring_create_invoice(self, date_ref=None):
        """
        Cron: invoice contracts in batch
        """
        return super(
            ContractContract, self.with_context(batch=True)
        ).cron_recurring_create_invoice(date_ref)

    def _recurring_create_invoice(self, date_ref=False):
        if self.env.context.get("batch", False):
            for records, description in self._split_to_invoicing_chunks():
                description = f"Automated {description}"
                (
                    super(ContractContract, records)
                    .with_delay(description=description)
                    ._recurring_create_invoice(date_ref)
                )
            return
        return super()._recurring_create_invoice(date_ref)

    def _split_to_invoicing_chunks(self):
        contracts = self
        num_recs = len(contracts)
        chunk_size = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(CONTRACT_INVOICING_CHUNK_SIZE, default=0)
        )
        if chunk_size < 1:
            chunk_size = num_recs
        chunks = []
        for batch_number, chunk_records in enumerate(
            tools.split_every(chunk_size, contracts.ids, contracts.browse), start=1
        ):
            from_rec = (batch_number - 1) * chunk_size + 1
            to_rec = min(from_rec + chunk_size - 1, num_recs)
            description = (
                f"Batch Invoice Contracts - {batch_number} "
                f"({from_rec}-{to_rec}/{num_recs})"
            )
            chunks.append((chunk_records, description))
        return chunks
