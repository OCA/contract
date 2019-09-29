# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from ..tools import _default_sequence


class AgreementParameterValue(models.Model):
    _name = 'agreement.parameter.value'
    _description = 'Possible values for agreement m2o parameters'
    _order = "parameter, sequence"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(
        required=True,
        index=True,
        help="code of the value, can be used to search for it "
        "in a language neutral way",
    )
    sequence = fields.Integer(
        required=True,
        default=_default_sequence,
        help="order the values for a given parameter",
    )
    parameter = fields.Char(
        required=True,
        help='set to the name of the agreement field which '
        'can have this value (not strictly required but it helps)',
    )
    is_default = fields.Boolean(
        string="Is the default value?",
        help="Set this on 1 record for a given parameter to flag the value as "
        "the default value. If a parameter has no default value, then its "
        "default is False",
    )

    @api.model
    def get(self, parameter, code):
        res = self.search(
            [('parameter', '=', parameter), ('code', '=', code)], limit=1
        )
        if res:
            return res
        else:
            raise ValueError((parameter, code))

    @api.model
    def get_default(self, parameter):
        res = self.search(
            [('parameter', '=', parameter), ('is_default', '=', True)], limit=1
        )
        return res or False
