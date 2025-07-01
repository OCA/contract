from odoo import models


class SaleSubscription(models.Model):
    _inherit = "sale.order.line"

    def get_subscription_line_values(self):
        res = super().get_subscription_line_values()

        if not res["analytic_distribution"]:
            if self.project_id.analytic_account_id:
                res["analytic_distribution"] = {
                    self.project_id.analytic_account_id.id: 100.0
                }

        return res
