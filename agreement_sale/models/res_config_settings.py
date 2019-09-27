from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_use_agreement_type = fields.Boolean(
        'Use agreement types',
        implied_group='agreement.group_use_agreement_type'
    )
    group_use_agreement_template = fields.Boolean(
        'Use agreement template',
        implied_group='agreement.group_use_agreement_template'
    )
