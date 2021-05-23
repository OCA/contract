# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = 'res.company'

    create_contract_at_sale_order_confirmation = fields.Boolean(
        string="Automatically Create Contracts At Sale Order Confirmation",
        default=True,
    )

    standard_quantity_for_creation_contract_by_sale_order = fields.Selection(
        string="Standard Quantity For Contract Creation By Sales Order",
        selection=[
            ('one', 'Create contracts with quantity equal to 1'),
            ('sale_order_line', 'Create contracts with quantity from the sales '
                                'order line.'),
        ],
        help='One: Create contracts with quantity equal to 1\n'
             'Sale Order Line: Create contracts with quantity from the sales '
             'order line.',
        default="one",
    )
