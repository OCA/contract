# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractAbstractContract(models.AbstractModel):
    _inherit = 'contract.abstract.contract'

    type = fields.Selection(
        [('invoice', 'Invoice'),
         ('sale', 'Sale')],
        string='Type',
        default='invoice',
        required=True,
    )
    sale_autoconfirm = fields.Boolean(
        string='Sale Autoconfirm')
