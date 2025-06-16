# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ContractLine(models.Model):
    _inherit = "contract.line"

    def _prepare_invoice_line(self):
        vals = super()._prepare_invoice_line()
        vals["discount_fixed"] = self.discount_fixed
        return vals
