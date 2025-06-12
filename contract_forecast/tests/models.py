from odoo import fields, models


class Contract(models.Model):
    "Added model to test write and _get_forecast_update_trigger_fields methods"

    # pylint: disable=consider-merging-classes-inherited
    _inherit = "contract.contract"

    dummy = fields.Boolean(default=False)

    def _get_forecast_update_trigger_fields(self):
        result = super()._get_forecast_update_trigger_fields()
        result.append("dummy")
        return result
