# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agreement_id = fields.Many2one(
        comodel_name='agreement', string='Agreement', ondelete='restrict',
        track_visibility='onchange', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
