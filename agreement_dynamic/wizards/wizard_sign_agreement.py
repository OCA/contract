from odoo import fields, models


class WizardSignAgreement(models.TransientModel):
    _name = "wizard.sign.agreement"
    _description = "Provide signature date for agreement"

    agreement_id = fields.Many2one("agreement", "Agreement")
    signature_date = fields.Date(
        string="Lock Date", default=fields.Date.today(), required=True
    )

    def action_sign_agreement(self):
        """Sign the agreement on given date"""
        self.ensure_one()
        self.agreement_id.signature_date = self.signature_date
