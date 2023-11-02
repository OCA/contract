# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    rebate_type = fields.Selection(
        selection=[
            ("global", "Global (A discount global for all lines)"),
            ("line", "Line (A discount for every line)"),
            ("section_total", "Compute total and apply discount rule match"),
            ("section_prorated", "Calculate the discount in each amount section"),
        ],
        string="rebate type",
    )
    rebate_line_ids = fields.One2many(
        comodel_name="agreement.rebate.line",
        string="Agreement rebate lines",
        inverse_name="agreement_id",
        copy=True,
    )
    rebate_section_ids = fields.One2many(
        comodel_name="agreement.rebate.section",
        string="Agreement rebate sections",
        inverse_name="agreement_id",
        copy=True,
    )
    rebate_discount = fields.Float()
    is_rebate = fields.Boolean(
        related="agreement_type_id.is_rebate", string="Is rebate agreement type"
    )
    additional_consumption = fields.Float(default=0.0)


class AgreementRebateLine(models.Model):
    _name = "agreement.rebate.line"
    _description = "Agreement Rebate Lines"

    agreement_id = fields.Many2one(comodel_name="agreement", string="Agreement")
    rebate_target = fields.Selection(
        [
            ("product", "Product variant"),
            ("product_tmpl", "Product templates"),
            ("category", "Product categories"),
            ("condition", "Rebate condition"),
            ("domain", "Rebate domain"),
        ]
    )
    rebate_product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Products",
    )
    rebate_product_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        string="Product templates",
    )
    rebate_category_ids = fields.Many2many(
        comodel_name="product.category",
        string="Product categories",
    )
    rebate_condition_id = fields.Many2one(
        comodel_name="agreement.rebate.condition",
        string="Rebate condition",
    )
    rebate_domain = fields.Char(
        compute="_compute_rebate_domain",
        store=True,
        readonly=False,
    )
    rebate_discount = fields.Float()

    @api.depends(
        "rebate_target",
        "rebate_product_ids",
        "rebate_product_tmpl_ids",
        "rebate_category_ids",
        "rebate_condition_id",
    )
    def _compute_rebate_domain(self):
        for line in self:
            rebate_domain = []
            if line.rebate_target == "product":
                rebate_domain = [("product_id", "in", line.rebate_product_ids.ids)]
            elif line.rebate_target == "product_tmpl":
                rebate_domain = [
                    (
                        "product_id.product_tmpl_id",
                        "in",
                        line.rebate_product_tmpl_ids.ids,
                    )
                ]
            elif line.rebate_target == "category":
                rebate_domain = [
                    ("product_id.categ_id", "in", line.rebate_category_ids.ids)
                ]
            elif line.rebate_target == "condition":
                rebate_domain = line.rebate_condition_id.rebate_domain or []
            line.rebate_domain = str(rebate_domain)


class AgreementRebateCondition(models.Model):
    _name = "agreement.rebate.condition"
    _description = "Agreement Rebate Condition"

    name = fields.Char(string="Rebate condition")
    rebate_domain = fields.Char(string="Domain")


class AgreementRebateSection(models.Model):
    _name = "agreement.rebate.section"
    _description = "Agreement Rebate Section"

    agreement_id = fields.Many2one(comodel_name="agreement", string="Agreement")
    amount_from = fields.Float(string="From")
    amount_to = fields.Float(string="To")
    rebate_discount = fields.Float(string="% Dto")
