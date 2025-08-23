# Copyright 2025 Eska Yazılım ve Danışmanlık A.Ş (www.eskayazilim.com.tr)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    termination_notice_interval = fields.Integer(
        default=1, string="Termination Notice Before"
    )
    termination_notice_rule_type = fields.Selection(
        [("daily", "Day(s)"), ("weekly", "Week(s)"), ("monthly", "Month(s)")],
        default="monthly",
        string="Termination Notice type",
    )
    automatic_price = fields.Boolean(
        string="Auto-price?",
        default=False,
        help=(
            "If checked, the price will be taken from the pricelist. "
            "Otherwise, it must be set manually."
        ),
    )
    manual_renew_needed = fields.Boolean(
        string="Manual Renenew Needed",
        default=False,
        help="This flag is used to make a difference between a definitive stop"
        "and temporary one for which a user is not able to plan a"
        "successor in advance",
    )
