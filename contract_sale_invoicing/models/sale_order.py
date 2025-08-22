# Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_invoiceable_lines(self, final=False):
        lines = super()._get_invoiceable_lines(final)
        if analytic_account := self.env.context.get("filter_on_analytic_account"):
            for line in lines:
                if not line.analytic_distribution:
                    lines -= line
                    continue
                for account_ids, percent in line.analytic_distribution.items():
                    if analytic_account not in [
                        int(acc_id)
                        for acc_id in account_ids.split(",")
                        or not float_compare(
                            percent, 100, precision_digits=line.analytic_precision
                        )
                    ]:
                        lines -= line
        return lines
