# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestContractSale(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_obj = cls.env["product.product"]
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
        # Create the product that will be sold on the contract
        vals = {
            "name": "Product 1",
        }
        cls.product = cls.product_obj.create(vals)

        # Create the customer contract
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": cls.partner.id,
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "group_id": cls.analytic_account.id,
            }
        )
        with Form(cls.contract) as contract_form, freeze_time(contract_date):
            # Create two lines, one with a section, one with a product
            with contract_form.contract_line_ids.new() as line_form:
                line_form.name = ""
                line_form.display_type = "line_section"
            with contract_form.contract_line_ids.new() as line_form:
                line_form.product_id = cls.product
                line_form.name = "Contract test from #START# to #END#"
                line_form.quantity = 1
                line_form.recurring_rule_type = "weekly"
                line_form.recurring_interval = 1
                line_form.date_start = "2020-01-15"
                line_form.recurring_next_date = "2020-01-15"
        cls.section_line = cls.contract.contract_line_ids[0]
        cls.product_line = cls.contract.contract_line_ids[1]

    def test_contract_line_section(self):
        date_ref = self.contract.recurring_next_date
        invoice_vals, move_form = self.contract._prepare_invoice(date_ref)
        res = self.section_line._prepare_invoice_line(move_form)
        self.assertEqual(res["show_details"], True)
        self.assertEqual(res["show_subtotal"], True)
        self.product_line.write({"show_details": False, "show_subtotal": False})
        res = self.product_line._prepare_invoice_line(move_form)
        self.assertEqual(res["product_id"], self.product.id)
        self.assertEqual(res["show_details"], False)
        self.assertEqual(res["show_subtotal"], False)
