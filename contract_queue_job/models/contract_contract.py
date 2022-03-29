# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

from odoo.addons.queue_job.job import job

QUEUE_CHANNEL = "root.CONTRACT_INVOICE"


class ContractContract(models.Model):

    _inherit = "contract.contract"

    @api.multi
    @job(default_channel=QUEUE_CHANNEL)
    def _recurring_create_invoice(self, date_ref=False):
        res = self.env["account.invoice"]
        if len(self) > 1:
            for rec in self:
                rec.with_delay()._recurring_create_invoice(date_ref=date_ref)
            return res
        return super()._recurring_create_invoice(date_ref=date_ref)
