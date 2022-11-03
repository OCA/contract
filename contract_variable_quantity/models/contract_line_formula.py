# Copyright 2016 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.tools.safe_eval import safe_eval


class ContractLineFormula(models.Model):
    _name = "contract.line.qty.formula"
    _description = "Contract Line Formula"

    name = fields.Char(required=True, translate=True)
    code = fields.Text(required=True, default="result = 0")

    @api.constrains("code")
    def _check_code(self):
        eval_context = {
            "env": self.env,
            "context": self.env.context,
            "user": self.env.user,
            "line": self.env["contract.line"],
            "contract": self.env["contract.contract"],
            "invoice": self.env["account.move"],
            "quantity": 0,
            "period_first_date": False,
            "period_last_date": False,
            "invoice_date": False,
        }
        try:
            safe_eval(self.code.strip(), eval_context, mode="exec", nocopy=True)
        except Exception as e:
            raise exceptions.ValidationError(
                _("Error evaluating code.\nDetails: %s") % e
            ) from e
        if "result" not in eval_context:
            raise exceptions.ValidationError(_("No valid result returned."))
