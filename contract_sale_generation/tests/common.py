# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo import fields
from odoo.tests import Form


def to_date(date):
    return fields.Date.to_date(date)


class ContractSaleCommon:
    # Use case : Prepare some data for current test case

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Contracts",
            }
        )
        cls.payment_term_id = cls.env.ref(
            "account.account_payment_term_end_following_month"
        )
        cls.fiscal_position_id = cls.env["account.fiscal.position"].create(
            {"name": "Contracts"}
        )
        contract_date = "2020-01-15"
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "pricelist for contract test",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "partner test contract",
                "property_product_pricelist": cls.pricelist.id,
                "property_payment_term_id": cls.payment_term_id.id,
                "property_account_position_id": cls.fiscal_position_id.id,
            }
        )
        cls.product_1 = cls.env.ref("product.product_product_1")
        cls.product_1.taxes_id += cls.env["account.tax"].search(
            [("type_tax_use", "=", "sale")], limit=1
        )
        cls.product_1.description_sale = "Test description sale"
        cls.line_template_vals = {
            "product_id": cls.product_1.id,
            "name": "Test Contract Template",
            "quantity": 1,
            "uom_id": cls.product_1.uom_id.id,
            "price_unit": 100,
            "discount": 50,
            "recurring_rule_type": "yearly",
            "recurring_interval": 1,
        }
        cls.template_vals = {
            "name": "Test Contract Template",
            "contract_type": "sale",
            "contract_line_ids": [
                (0, 0, cls.line_template_vals),
            ],
        }
        cls.template = cls.env["contract.template"].create(cls.template_vals)
        # For being sure of the applied price
        cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "product_id": cls.product_1.id,
                "compute_price": "formula",
                "base": "list_price",
            }
        )
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": cls.partner.id,
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "generation_type": "sale",
                "sale_autoconfirm": False,
                "group_id": cls.analytic_account.id,
                "date_start": "2020-01-15",
            }
        )
        cls.line_vals = {
            "name": "Services from #START# to #END#",
            "quantity": 1,
            "price_unit": 100,
            "discount": 50,
            "recurring_rule_type": "monthly",
            "recurring_interval": 1,
            "date_start": "2020-01-01",
            "recurring_next_date": "2020-01-15",
        }
        with Form(cls.contract) as contract_form, freeze_time(contract_date):
            contract_form.contract_template_id = cls.template
            with contract_form.contract_line_ids.new() as line_form:
                line_form.product_id = cls.product_1
                line_form.name = "Services from #START# to #END#"
                line_form.quantity = 1
                line_form.price_unit = 100.0
                line_form.discount = 50
                line_form.recurring_rule_type = "monthly"
                line_form.recurring_interval = 1
                line_form.date_start = "2020-01-15"
                line_form.recurring_next_date = "2020-01-15"
        cls.contract_line = cls.contract.contract_line_ids[1]

        cls.contract2 = cls.env["contract.contract"].create(
            {
                "name": "Test Contract 2",
                "generation_type": "sale",
                "partner_id": cls.partner.id,
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "contract_type": "purchase",
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_1.id,
                            "name": "Services from #START# to #END#",
                            "quantity": 1,
                            "uom_id": cls.product_1.uom_id.id,
                            "price_unit": 100,
                            "discount": 50,
                            "recurring_rule_type": "monthly",
                            "recurring_interval": 1,
                            "date_start": "2018-02-15",
                            "recurring_next_date": "2018-02-22",
                        },
                    )
                ],
            }
        )
