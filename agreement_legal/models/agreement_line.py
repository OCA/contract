# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AgreementLine(models.Model):
    _name = "agreement.line"
    _description = "Agreement Lines"

    product_id = fields.Many2one("product.product", string="Product")
    name = fields.Char(string="Description", required=True)
    agreement_id = fields.Many2one("agreement", string="Agreement", ondelete="cascade")
    qty = fields.Float(string="Quantity")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure", required=True)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.name = self.product_id.name
        self.uom_id = self.product_id.uom_id.id
