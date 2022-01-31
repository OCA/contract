# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo import fields
from odoo.tests import Form
from odoo.tests.common import SavepointCase


def to_date(date):
    return fields.Date.to_date(date)


class TestContractSalePikcingNote(SavepointCase):
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
            }
        )
        cls.product_1 = cls.env.ref("product.product_product_10")
        cls.product_1.taxes_id += cls.env["account.tax"].search(
            [("type_tax_use", "=", "sale")], limit=1
        )
        cls.line_template_vals = {
            "product_id": cls.product_1.id,
            "name": "Test Contract Template",
            "quantity": 1,
            "uom_id": cls.product_1.uom_id.id,
            "price_unit": 100,
            "discount": 50,
            "recurring_rule_type": "monthly",
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
                "picking_note": "Careful with boxes",
                "picking_customer_note": "Deliver at door",
            }
        )
        with Form(cls.contract) as contract_form, freeze_time(contract_date):
            contract_form.contract_template_id = cls.template
            with contract_form.contract_line_ids.new() as line_form:
                line_form.product_id = cls.product_1
                line_form.name = "Cabinets from #START# to #END#"
                line_form.quantity = 1
                line_form.price_unit = 100.0
                line_form.discount = 50
                line_form.recurring_rule_type = "monthly"
                line_form.recurring_interval = 1
                line_form.date_start = "2020-01-15"
                line_form.recurring_next_date = "2020-01-15"
        cls.contract_line = cls.contract.contract_line_ids[1]

    def test_contract_delivery(self):
        self.assertAlmostEqual(self.contract_line.price_subtotal, 50.0)
        self.contract_line._onchange_product_id()
        self.contract_line.price_unit = 100.0
        self.contract.partner_id = self.partner.id
        self.contract.recurring_create_sale()
        self.sale = self.contract._get_related_sales()
        self.assertEqual(self.sale.picking_note, "Careful with boxes")
        self.assertEqual(self.sale.picking_customer_note, "Deliver at door")
