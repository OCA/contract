from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools import safe_eval


class Contract(models.Model):
    _inherit = "hr.contract"

    agreement_ids = fields.One2many("agreement", "contract_id")

    def action_create_agreement(self):
        self.ensure_one()
        # search for agreement templates
        templates = self.env["agreement"].search(
            [("model_id.model", "=", self._name), ("is_template", "=", True)]
        )
        eligible_template = self.env["agreement"]
        for template in templates:
            # Check the template global domain
            if not self._check_template(template):
                continue
            eligible_template += template
        if not eligible_template:
            raise UserError(_("No matching templates found"))
        if len(eligible_template) > 1:
            raise UserError(_("More templates than one found"))
        agreement = eligible_template.copy()
        # Transform this into an agreement,
        # tailor made for this contract
        agreement.write(
            {
                "is_template": False,
                "res_id": self.id,
                "contract_id": self.id,
                "partner_id": self.employee_id.user_partner_id.id,
                "template_id": eligible_template.id,
            }
        )
        return {
            "name": _("Agreement"),
            "view_mode": "form",
            "res_model": "agreement",
            "type": "ir.actions.act_window",
            # new, because we want to save the form
            "target": "new",
            "res_id": agreement.id,
        }

    def _check_template(self, template):
        return self in self.search(safe_eval(template.condition_domain_global))
