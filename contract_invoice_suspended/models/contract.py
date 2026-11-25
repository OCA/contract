# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Contract(models.Model):
    _inherit = "contract.contract"

    is_auto_invoice_suspended = fields.Boolean(
        string="Automatic invoicing suspended",
        store=True,
        tracking=True,
        compute="_compute_is_auto_invoice_suspended",
        inverse="_inverse_is_auto_invoice_suspended",
    )
    auto_invoice_suspended_user_id = fields.Many2one(
        string="Automatic invoicing suspended by",
        comodel_name="res.users",
        readonly=True,
    )
    auto_invoice_suspended_date = fields.Date(
        string="Automatic invoicing suspended on", readonly=True
    )
    auto_invoice_suspended_reason_id = fields.Many2one(
        string="Automatic invoicing suspended reason",
        comodel_name="contract.automatic.invoice.suspension.reason",
        domain=[("can_be_selected", "=", True)],
    )
    suspended_reason_category_id = fields.Many2one(
        comodel_name="contract.automatic.invoice.suspension.reason",
        related="auto_invoice_suspended_reason_id.suspended_reason_category_id",
        store=True,
    )

    @api.model
    def _get_contracts_to_invoice_domain(self, date_ref=None):
        res = super()._get_contracts_to_invoice_domain(date_ref=date_ref)
        res.append(("is_auto_invoice_suspended", "=", False))
        return res

    @api.depends("auto_invoice_suspended_user_id")
    def _compute_is_auto_invoice_suspended(self):
        self.filtered("auto_invoice_suspended_user_id").update(
            {"is_auto_invoice_suspended": True}
        )

    def _inverse_is_auto_invoice_suspended(self):
        if self.is_auto_invoice_suspended:
            self.write(
                {
                    "auto_invoice_suspended_user_id": self.env.user.id,
                    "auto_invoice_suspended_date": fields.Date.today(),
                }
            )
        else:
            self.write(
                {
                    "auto_invoice_suspended_user_id": False,
                    "auto_invoice_suspended_date": False,
                }
            )
