# Copyright 2021 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirm", "Confirmed"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        readonly=True,
        copy=False,
        index=True,
        default="draft",
    )

    def action_draft(self):
        self.write({"state": "draft"})

    def action_confirm(self):
        self.write({"state": "confirm"})

    def action_cancel(self):
        self.write({"state": "cancel"})
