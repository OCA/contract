# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields


class AgreementType(models.Model):
    _inherit = 'agreement.type'

    journal_type = fields.Selection(
        selection=[
            ('sale', 'Rappel Sales'),
        ],
        string='Journal type',
        default='sale',
    )
