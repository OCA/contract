# Copyright 2026 Domatix - Alvaro Domatix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import format_date


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    subscription_period_date_format = fields.Char(
        string="Subscription period date format",
        config_parameter="subscription_oca.period_date_format",
        help="Babel date format used to display the billed period on the "
        "invoice line description, e.g. dd/MM/yyyy. Leave empty to format "
        "the dates according to the customer language.",
    )

    @api.constrains("subscription_period_date_format")
    def _check_subscription_period_date_format(self):
        """Reject values that Babel cannot render: a broken pattern here would
        crash invoice generation (and the cron swallows that error silently),
        so it must fail fast, at the moment the user can still fix it."""
        for record in self:
            fmt = record.subscription_period_date_format
            if not fmt:
                continue
            try:
                format_date(self.env, fields.Date.today(), date_format=fmt)
            except Exception as error:
                raise ValidationError(
                    self.env._(
                        "The subscription period date format is not a valid "
                        "Babel date pattern (e.g. dd/MM/yyyy). %(error)s",
                        error=error,
                    )
                ) from error
