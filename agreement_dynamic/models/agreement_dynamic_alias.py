from odoo import fields, models


class AgreementDynamicAlias(models.Model):
    _name = "agreement.dynamic.alias"
    _description = "Replace expressions before rendering"

    expression_from = fields.Char(
        required=True, help="Look for this in agreement_id.section_ids.content"
    )
    expression_to = fields.Char(
        required=True, help="Replace with this in agreement_id.section_ids.content"
    )
    is_active = fields.Boolean(
        "Active", default=True, help="To use the record when prerendering"
    )
