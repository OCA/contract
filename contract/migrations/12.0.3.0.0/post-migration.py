# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info(">> Post-Migration 12.0.3.0.0")
    _logger.info("Populate invoicing partner field on contracts")
    env = api.Environment(cr, SUPERUSER_ID, {})
    contracts = env["account.analytic.account"].search([])
    contracts._inverse_partner_id()
