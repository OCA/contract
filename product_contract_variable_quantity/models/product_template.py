# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    qty_type = fields.Selection(
        selection=[
            ('fixed', 'Fixed quantity'),
            ('variable', 'Variable quantity'),
        ],
        required=False,
        default='fixed',
        string="Qty. type",
    )
    qty_formula_id = fields.Many2one(
        comodel_name="contract.line.qty.formula", string="Qty. formula"
    )

    @api.onchange('is_contract')
    def _change_is_contract(self):
        """ Clear the relation to contract_template_id when downgrading
        product from contract
        """
        res = super(ProductTemplate, self)._change_is_contract()
        if not self.is_contract:
            self.qty_type = False
            self.qty_formula_id = False
        return res
