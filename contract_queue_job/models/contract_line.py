# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from odoo.addons.queue_job.job import job

QUEUE_CHANNEL = "root.CONTRACT_LINE_RENEW"


class ContractLine(models.Model):

    _inherit = "contract.line"

    @job(default_channel=QUEUE_CHANNEL)
    def renew(self):
        if len(self) > 1:
            for rec in self:
                rec.with_delay().renew()
            return self.env["contract.line"]
        return super().renew()
