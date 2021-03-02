# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class CreateAgreementWizard(models.TransientModel):
    _name = "create.agreement.wizard"
    _description = "Create Agreement Wizard"

    template_id = fields.Many2one(
        comodel_name="agreement",
        string="Template",
        required=True,
        domain="[('is_template', '=', True)]",
    )

    @api.multi
    def create_agreement(self):
        self.ensure_one()
        res = self.template_id.create_new_agreement()
        return res
