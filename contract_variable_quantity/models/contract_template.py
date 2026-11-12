# Copyright 2016 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractTemplate(models.Model):
    """Hold the setting on the template so it can be preset.

    ``contract.contract`` inherits ``contract.template``, so it keeps the
    field, and ``_onchange_contract_template_id`` copies the value over when
    a template is selected.
    """

    _inherit = "contract.template"

    skip_zero_qty = fields.Boolean(
        string="Skip Zero Qty Lines",
        help="If checked, contract lines with 0 qty don't create invoice line",
    )
