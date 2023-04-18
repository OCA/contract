# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ast

from odoo import models


class ContractLine(models.Model):

    _inherit = "contract.line"

    def renew(self):
        as_job = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("contract.queue.job", default=False)
        )

        try:
            as_job = ast.literal_eval(as_job) if as_job else False
        except ValueError:
            as_job = False

        if as_job and len(self) > 1:
            for rec in self:
                rec.with_delay().renew()
            return self.env["contract.line"]
        return super().renew()
