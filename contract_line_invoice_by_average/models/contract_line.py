# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractLine(models.Model):
    _inherit = 'contract.line'

    products_invoiced_by_avg_ids = fields.Many2many(
        comodel_name='product.product',
        relation='contract_line_product_id_rel',
        column1='contract_line_id',
        column2='product_id',
        string='Products Invoiced using Average Quantity')
