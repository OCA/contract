# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models
from ..tools import _default_sequence


class AgreementType(models.Model):
    _inherit = 'agreement.type'

    _description = 'Types of sale agreement policies'
    _order = 'sequence, code'

    code = fields.Char(index=True)
    sequence = fields.Integer(index=True, default=_default_sequence)
    active = fields.Boolean(default=True)

    default_agreement_id = fields.Many2one(
        'agreement',
        string="Default Agreement",
        domain=[('is_template', '=', True)],
    )

    @api.constrains('default_agreement_id')
    def _check_code_agreement(self):
        for rec in self:
            if rec.default_agreement_id.agreement_type_id != rec:
                msg = _(
                    'The type of the default agreement must be %s, not %s'
                ) % (rec.name, rec.default_agreement_id.agreement_type_id.name)
                raise exceptions.ValidationError(msg)
