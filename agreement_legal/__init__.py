# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID
from . import models


def post_init_agreement_legal(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, dict())
    cr.execute('UPDATE agreement SET stage_id = %s WHERE stage_id IS NULL;',
               (env.ref('agreement_legal.agreement_stage_new').id,))
    return True
