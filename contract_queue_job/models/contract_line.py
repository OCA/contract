# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ContractLine(models.Model):
    _inherit = "contract.line"

    def renew(self):
        if len(self) > 1:
            for rec in self:
                rec.with_delay().renew()
            return self.env["contract.line"]
        return super().renew()
