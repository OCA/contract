# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class Agreement(models.Model):
    _inherit = 'agreement'

    req_so_delivery_lead_time = fields.Many2one(
        'agreement.parameter.value',
        string='Order kept open',
        domain=[
            ('parameter', '=',
             'req_so_delivery_lead_time')
        ],
    )
    req_so_transport = fields.Many2one(
        'agreement.parameter.value',
        string='Back order shipment',
        domain=[
            ('parameter', '=', 'req_so_transport')
        ],
    )
    req_cust_delivery_window = fields.Many2one(
        'agreement.parameter.value',
        string='Partial deliveries',
        domain=[('parameter', '=', 'req_cust_delivery_window')],
    )
    req_cust_preadvice = fields.Many2one(
        'agreement.parameter.value',
        string='Partial deliveries',
        domain=[('parameter', '=', 'req_cust_preadvice')],
    )
    
    @api.model
    def _get_customer_agreement_fields(self):
        return super()._get_customer_agreement_fields() + [
            'req_cust_preadvice',
            'req_cust_delivery_window',
        ]

    @api.model
    def _get_sale_agreement_fields(self):
        return super()._get_sale_agreement_fields() + [
            'req_so_transport',
            'req_so_delivery_lead_time',
        ]
