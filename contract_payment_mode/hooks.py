# Copyright 2016 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Copy payment mode from partner to the new field at contract."""
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        m_contract = env["contract.contract"]
        contracts = m_contract.search([("payment_mode_id", "=", False)])
        if contracts:
            _logger.info("Setting payment mode: %d contracts" % len(contracts))
        for contract in contracts:
            payment_mode = contract.partner_id.customer_payment_mode_id
            if payment_mode:
                contract.payment_mode_id = payment_mode.id
        _logger.info("Setting payment mode: Done")
