from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Agreement(models.Model):
    _inherit = "agreement"

    contract_id = fields.Many2one("hr.contract")
