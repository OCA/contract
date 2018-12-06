# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class Agreement(models.Model):
    _inherit = 'agreement'

    service_order_count = fields.Integer(
        compute='_compute_service_order_count',
        string='# Service Orders'
    )

    @api.multi
    def _compute_service_order_count(self):
        for agreement in self:
            res = self.env['fsm.order'].search_count(
                [('agreement_id', '=', agreement.id)])
            agreement.service_order_count = res or 0

    @api.multi
    def action_view_service_order(self):
        for agreement in self:
            fsm_order_ids = self.env['fsm.order'].search(
                [('agreement_id', '=', agreement.id)])
            action = self.env.ref(
                'fieldservice.action_fsm_operation_order').read()[0]
            if len(fsm_order_ids) > 1:
                action['domain'] = [('id', 'in', fsm_order_ids.ids)]
            elif len(fsm_order_ids) == 1:
                action['views'] = [(
                    self.env.ref('fieldservice.fsm_order_form').id,
                    'form')]
                action['res_id'] = fsm_order_ids.ids[0]
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action
