# Copyright 2023 Akretion - Florian Mounier
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractIncrease(models.Model):
    _name = "contract.increase"
    _description = "Contract Increase"

    contract_id = fields.Many2one(
        comodel_name="contract.contract",
        string="Contract",
        required=True,
        ondelete="cascade",
    )
    date = fields.Date(string="Date of increase", required=True)
    application_date = fields.Date(string="Date of application", readonly=True)
    rate = fields.Float(string="Rate of increase", required=True)
    description = fields.Text(string="Description")

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        related="contract_id.partner_id",
    )
