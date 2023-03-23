# Copyright 2023 Jaime Millan (<https://xtendoo.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Warehouse",
        store=True,
        readonly=False,
    )

    def _prepare_sale(self, date_ref):
        values = super()._prepare_sale(date_ref)
        if self.warehouse_id:
            values["warehouse_id"] = self.warehouse_id.id
        return values
