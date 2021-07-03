# Copyright 2021 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ExceptionRule(models.Model):
    _inherit = "exception.rule"

    agreement_ids = fields.Many2many(comodel_name="agreement", string="Agreements")
    model = fields.Selection(
        selection_add=[
            ("agreement", "Agreement"),
            ("agreement.line", "Agreement line"),
        ],
        ondelete={"agreement": "cascade", "agreement.line": "cascade"},
    )
