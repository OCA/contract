# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_contract = fields.Boolean('Is a contract')
    property_contract_template_id = fields.Many2one(
        comodel_name='contract.template',
        string='Contract Template',
        company_dependent=True,
    )
    default_qty = fields.Integer(string="Default Quantity", default=1)
    recurring_rule_type = fields.Selection(
        [
            ('daily', 'Day(s)'),
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('monthlylastday', 'Month(s) last day'),
            ('quarterly', 'Quarter(s)'),
            ('semesterly', 'Semester(s)'),
            ('yearly', 'Year(s)'),
        ],
        default='monthly',
        string='Invoice Every',
        help="Specify Interval for automatic invoice generation.",
    )
    recurring_invoicing_type = fields.Selection(
        [('pre-paid', 'Pre-paid'), ('post-paid', 'Post-paid')],
        default='pre-paid',
        string='Invoicing type',
        help="Specify if process date is 'from' or 'to' invoicing date",
    )
    is_auto_renew = fields.Boolean(string="Auto Renew", default=False)
    termination_notice_interval = fields.Integer(
        default=1, string='Termination Notice Before'
    )
    termination_notice_rule_type = fields.Selection(
        [('daily', 'Day(s)'), ('weekly', 'Week(s)'), ('monthly', 'Month(s)')],
        default='monthly',
        string='Termination Notice type',
    )
    auto_renew_interval = fields.Integer(
        default=1,
        string='Renew Every',
        help="Renew every (Days/Week/Month/Year)",
    )
    auto_renew_rule_type = fields.Selection(
        [
            ('daily', 'Day(s)'),
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('yearly', 'Year(s)'),
        ],
        default='yearly',
        string='Renewal type',
        help="Specify Interval for automatic renewal.",
    )

    def create_variant_ids(self):
        result = super(ProductTemplate, self).create_variant_ids()
        self._set_variant_ids_contract()
        return result

    def _set_variant_ids_contract(self, remove=False):
        """If we modify the attributes, variants might get archived or created.
           When that happens, we must check we transfered the contract template
           from the template to the variant, in each company.
        """
        to_process = self if remove else self.filtered("is_contract")
        for company in self.env["res.company"].search([]):
            tmpls_in_company = to_process.with_context(force_company=company.id)
            for template in tmpls_in_company:
                if remove:
                    variants = template.product_variant_ids
                    variants.write({"property_contract_template_id": False})
                else:
                    contract = template.property_contract_template_id
                    if contract:
                        for variant in template.product_variant_ids:
                            if not variant.property_contract_template_id:
                                variant.property_contract_template_id = contract
        if not remove:
            contracts_force_check = to_process.with_context(create_from_tmpl=False)
            contracts_force_check.mapped("product_variant_ids")._contract_constraint()

    @api.model
    def create(self, vals):
        if not vals.get("is_contract") and vals.get("property_contract_template_id"):
            error_message = _(
                "You cannot create a product with a contract template"
                " if this product is not a contract."
            )
            raise ValidationError(error_message)
        return super().create(vals)

    @api.multi
    def write(self, vals):
        """If we write on contract properties, we need to update the variants.
           We need to process differently the case when a product is_contract changes,
           or if we simply change its default contract template.
           Therefore we need to iterate on each template if we have a contract
           field in vals.
        """
        contract_key = "property_contract_template_id"
        if "is_contract" in vals or contract_key in vals:
            for template in self:
                is_contract = vals.get("is_contract")
                if is_contract is False and template.is_contract:  # remove contract
                    template_vals = {**vals, contract_key: False}
                    super(ProductTemplate, template).write(template_vals)
                    self._set_variant_ids_contract(remove=True)
                elif is_contract and not template.is_contract:  # set contract
                    super(ProductTemplate, template).write(vals)
                    template._set_variant_ids_contract()
                elif vals.get(contract_key):  # change contract
                    default_vars = template.mapped("product_variant_ids").filtered(
                        lambda v: v[contract_key] == template[contract_key]
                    )
                    default_vars.write({contract_key: vals[contract_key]})
                    super(ProductTemplate, template).write(vals)
                else:  # no real change to contract values
                    super(ProductTemplate, template).write(vals)
        else:
            super(ProductTemplate, self).write(vals)
        return True

    @api.constrains('is_contract', 'type')
    def _check_contract_product_type(self):
        """
        Contract product should be service type
        """
        if self.is_contract and self.type != 'service':
            raise ValidationError(_("Contract product should be service type"))
