# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class CreateAgreementWizard(models.TransientModel):
    _name = "create.agreement.wizard"
    _description = "Create Agreement Wizard"

    template_id = fields.Many2one(
        comodel_name="agreement",
        string="Template",
        required=True,
        domain="[('is_template', '=', True)]",
    )
    title = fields.Char(
        required=True,
    )

    def create_agreement(self):
        self.ensure_one()
        res = self.template_id.create_new_agreement()
        self._cr.execute(
            """
            update agreement set name = %s, description = %s where id = %s
        """,
            (self.title, self.title, res["res_id"]),
        )
        return res
