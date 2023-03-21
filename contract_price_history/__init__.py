# Copyright 2023 Akretion - Florian Mounier
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import models

from odoo import api, fields, SUPERUSER_ID


def _contract_line_price_history_post_init_hook(cr, registry):
    # At module install, we initialize the price history for each contract line
    env = api.Environment(cr, SUPERUSER_ID, {})
    contract_lines = env["contract.line"].search([])
    for cl in contract_lines:
        if not cl.price_history_ids:
            env["contract.line.price.history"].create(
                {
                    "new_price": cl.price_unit,
                    "date": fields.Date.today(),
                    "type": "unknown",
                    "contract_line_id": cl.id,
                }
            )
