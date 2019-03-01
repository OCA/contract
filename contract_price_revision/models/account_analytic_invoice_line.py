# Copyright 2019 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class AccountAnalyticINvoiceLine(models.Model):
    _inherit = "account.analytic.invoice.line"

    date_start = fields.Date(
        string='Start Date',
    )
    date_end = fields.Date(
        string='End Date',
    )
    previous_revision_id = fields.Many2one(
        comodel_name='account.analytic.invoice.line',
        string='Previous revision',
        help='Relation with previous revision',
    )
    previous_price = fields.Float(
        related='previous_revision_id.price_unit',
        readonly=True,
    )
    variation_percent = fields.Float(
        compute='_compute_variation_percent',
        store=True,
        digits=dp.get_precision('Product Price'),
        string='Variation %',
    )

    @api.multi
    @api.depends('price_unit', 'previous_revision_id.price_unit')
    def _compute_variation_percent(self):
        for line in self:
            if not (line.price_unit and line.previous_price):
                continue
            line.variation_percent = (
                (line.price_unit / line.previous_price - 1) * 100)
