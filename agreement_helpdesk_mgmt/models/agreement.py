# Copyright (C) 2019 - TODAY, Open Source Integrators
# Copyright (C) 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Agreement(models.Model):
    _inherit = 'agreement'

    ticket_ids = fields.One2many(
        'helpdesk.ticket',
        'agreement_id',
        string="Tickets"
    )

    ticket_count = fields.Integer(
        compute='_compute_ticket_count',
        string='# Tickets'
    )

    @api.depends('ticket_ids')
    def _compute_ticket_count(self):
        for rec in self:
            rec.ticket_count = len(
                rec.ticket_ids)

    @api.multi
    def action_view_ticket(self):
        for agreement in self:
            action = self.env.ref(
                'helpdesk_mgmt.helpdesk_ticket_action').read()[0]
            action['context'] = {}
            if len(self.ticket_ids) == 1:
                action['views'] = [(
                    self.env.ref('helpdesk_mgmt.ticket_view_form').id,
                    'form')]
                action['res_id'] = self.ticket_ids.ids[0]
            else:
                action['domain'] = [('id', 'in', self.ticket_ids.ids)]
            return action
