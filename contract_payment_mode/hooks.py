# Copyright 2016 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Copy payment mode from partner to the new field at contract."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    m_contract = env["contract.contract"]
    contracts = m_contract.search([("payment_mode_id", "=", False)])

    sale_contracts_to_update = contracts.filtered(
        lambda c: c.contract_type == "sale" and c.partner_id.customer_payment_mode_id
    )
    if sale_contracts_to_update:
        _logger.info(
            "Setting payment mode: %d sale contracts" % len(sale_contracts_to_update)
        )
    for contract in sale_contracts_to_update:
        contract.payment_mode_id = contract.partner_id.customer_payment_mode_id

    purchase_contracts_to_update = contracts.filtered(
        lambda c: c.contract_type == "purchase"
        and c.partner_id.supplier_payment_mode_id
    )
    if purchase_contracts_to_update:
        _logger.info(
            "Setting payment mode: %d purchase contracts"
            % len(purchase_contracts_to_update)
        )
    for contract in purchase_contracts_to_update:
        contract.payment_mode_id = contract.partner_id.supplier_payment_mode_id

    _logger.info("Setting payment mode: Done")
