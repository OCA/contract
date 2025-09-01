# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

CONTRACT_INVOICING_CHUNK_SIZE = "contract_invoicing_chunk_size"


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    contract_invoicing_chunk_size = fields.Integer(
        string="Invoicing Batch Size",
        config_parameter=CONTRACT_INVOICING_CHUNK_SIZE,
        default=100,
        help="Global parameter to determine how many contracts should be invoiced at "
        "once (0 to disable). To avoid server timeouts, the contracts will be "
        "invoiced in batches of this size.",
    )
