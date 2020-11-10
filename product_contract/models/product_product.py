# Copyright 2020 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    """Adds the possibility to override the template contract at variant level."""

    _inherit = "product.product"

    property_contract_template_id = fields.Many2one(
        comodel_name="contract.template",
        string="Contract Template",
        company_dependent=True,
    )

    def _format_names_for_constraint_message(self, limit=None):
        exceeds = limit and len(self) > limit
        to_format = self[:limit] if exceeds else self
        names = to_format.mapped("display_name")
        if exceeds:
            names.append(_("etc"))
        return _("\n - ").join(names)

    @api.constrains("property_contract_template_id", "is_contract")
    def _contract_constraint(self):
        if self.env.context.get("create_from_tmpl"):
            return  # in that case, constraint is checked after

        self._contract_constraint_template()
        if self.env["res.company"]._company_default_get().constrain_contract_products:
            self._contract_constraint_check()

    def _contract_constraint_check(self):
        contract_products = self.filtered("is_contract")
        bad_products = contract_products.filtered(
            lambda p: not p.property_contract_template_id
        )
        if bad_products:
            message_error = _(
                "Every contract product should have a contract template.\n"
                "Please check the following products:\n{}"
            ).format(bad_products._format_names_for_constraint_message(10))
            raise ValidationError(message_error)

    def _contract_constraint_template(self):
        products_with_contracts = self.filtered("property_contract_template_id")
        bad_products = products_with_contracts.filtered(lambda p: not p.is_contract)
        if bad_products:
            message_error = _(
                "Every product with a contract template should be a contract.\n"
                "Check the following products:\n{}"
            ).format(bad_products._format_names_for_constraint_message(10))
            raise ValidationError(message_error)
