from odoo import models


class Agreement(models.Model):
    _name = "agreement"
    _inherit = ["agreement", "archive.abstract"]
