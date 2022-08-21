# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    agreement_id = fields.Many2one(
        'agreement',
        string='Agreement',
    )
    serviceprofile_id = fields.Many2one('agreement.serviceprofile',
                                        'Service Profile')
