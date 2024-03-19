# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ContractAbstractContractLine(models.AbstractModel):
    _inherit = "contract.abstract.contract.line"

    discount_fixed = fields.Float(
        string="Discount (Fixed)",
        digits="Product Price",
        default=0.00,
        help="Fixed amount discount.",
    )

    @api.onchange("discount")
    def _onchange_discount(self):
        if self.discount:
            self.discount_fixed = 0.0

    @api.onchange("discount_fixed")
    def _onchange_discount_fixed(self):
        if self.discount_fixed:
            self.discount = 0.0

    @api.constrains("discount", "discount_fixed")
    def _check_only_one_discount(self):
        for rec in self:
            for line in rec:
                if line.discount and line.discount_fixed:
                    raise ValidationError(
                        _("You can only set one type of discount per line.")
                    )

    def _compute_price_subtotal_helper(self):
        self.ensure_one()
        subtotal = self.quantity * self.price_unit
        if self.discount:
            subtotal = super()._compute_price_subtotal_helper()
        elif self.discount_fixed:
            subtotal -= self.discount_fixed
        return subtotal

    @api.depends("quantity", "price_unit", "discount", "discount_fixed")
    def _compute_price_subtotal(self):
        super()._compute_price_subtotal()
