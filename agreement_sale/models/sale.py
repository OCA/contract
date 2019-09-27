# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agreement_id = fields.Many2one(
        comodel_name='agreement', string='Agreement', ondelete='restrict',
        track_visibility='onchange', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    agreement_type_id = fields.Many2one(
        comodel_name="agreement.type", string="Agreement Type",
        ondelete="restrict",
        track_visibility='onchange', readonly=True, copy=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
